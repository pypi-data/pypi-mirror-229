import copy
from os import makedirs
import shutil
from PIL import Image
import wandb
from leap_labs_test.event_handler import LeapLogger
from leap_labs_test.utils import *
from leap_labs_test.vega_charts import *
import numpy as np

np.set_printoptions(threshold=np.inf)


class Logger:
    def update(self, config, target_mask, objectives, transforms, base_classes, type):
        self.leap_logging = config.leap_logging
        self.config = config
        self.transforms = transforms
        self.type = type
        self.base_classes = base_classes
        self.base_class_labels = (
            "_".join(get_labels(base_classes, self.config.class_list))
            if base_classes is not None
            else ""
        )
        self.base_class_labels_str = (
            "base_" + self.base_class_labels + "_target_"
            if base_classes is not None
            else ""
        )

        self.target_mask = target_mask
        self.target_classes = [(t == 1).nonzero()[0].tolist()
                               for t in target_mask]
        self.target_class_labels = get_labels(
            self.target_classes, self.config.class_list
        )
        self.objective_names = [str(o).split(" ")[1] for o in objectives]
        self.transform_names = [str(t) for t in transforms]

        self.log_extra = "MOONWALK" in config.leap_api_key
        if self.log_extra:
            self.verbose = config.verbose
        else:
            self.verbose = 1
        if self.type == "baseline" and self.verbose == 1:
            self.verbose = 0

        self.file_path = f".leap_files/{type}_"
        makedirs(f".leap_files/", exist_ok=True)

    def __init__(self, config, target_mask, objectives, transforms, base_classes, type):
        self.update(config, target_mask, objectives,
                    transforms, base_classes, type)

        config_dict = vars(copy.copy(config))
        del config_dict["leap_api_key"]
        if "wandb_api_key" in config_dict.keys():
            del config_dict["wandb_api_key"]

        config_dict.update(
            {
                "objectives": self.objective_names,
                "transforms": self.transform_names,
                "base class labels": self.base_class_labels,
                "target class labels": self.target_class_labels,
                "type": type,
            }
        )

        if self.leap_logging:
            self.leap_run = LeapLogger(config.leap_api_key, config_dict)
            self.logging_fn = self.leap_run.log
        else:
            self.logging_fn = lambda s, d, f: None

        if config.wandb_api_key is not None:
            os.environ["WANDB_API_KEY"] = config.wandb_api_key
            os.environ["WANDB_SILENT"] = "true"

            wandb.init(
                entity=config.wandb_entity,
                project=config.project_name,
                reinit=True,
                config=config_dict,
            )

            def dual_log(step, data_log, file_log):
                if self.leap_logging:
                    self.leap_run.log(step, data_log, file_log)

                wandb_logs = {}
                for k, v in file_log.items():
                    if all(isinstance(item, LeapFile) for item in v):
                        wandb_logs[k] = [vi.to_wandb_image() for vi in v]
                    elif isinstance(v, LeapFile):
                        wandb_logs[k] = v.to_wandb_image()
                    else:
                        wandb_logs[k] = v

                for k, v in data_log.items():
                    if isinstance(v, LeapData):
                        wandb_logs[
                            k
                        ] = (
                            v.to_wandb()
                        )  # v.to_st(config.wandb_entity, config.project_name)
                    else:
                        wandb_logs[k] = v

                wandb.log(wandb_logs)

            self.logging_fn = dual_log

    def step_log(self, step, logits, probs, losses, return_log=False):
        if self.verbose < 2:
            return {}

        data_log = {
            f"{self.base_class_labels}_{self.type}_loss": {},
            f"{self.base_class_labels}_{self.type}_logits": {},
            f"{self.base_class_labels}_{self.type}_probs": {},
        }

        for o in range(len(self.objective_names)):
            data_log[self.objective_names[o]] = {
                self.target_class_labels[w]: losses[o][w].tolist()
                for w in range(len(self.target_classes))
            }
        for w in range(len(self.target_class_labels)):
            if losses is not None:
                data_log[f"{self.base_class_labels}_{self.type}_loss"].update(
                    {self.target_class_labels[w]: losses.mean(axis=0)[
                        w].tolist()}
                )
            # TODO this will just log the mean prob/logit, if there is more than one target per input.
            if self.type != "baseline":
                data_log[f"{self.base_class_labels}_{self.type}_probs"].update(
                    {
                        "target_{}_output_{}".format(
                            self.target_class_labels[w], self.target_class_labels[w]
                        ): probs[w, self.target_classes[w]]
                        .mean()
                        .tolist()
                    }
                )
                data_log[f"{self.base_class_labels}_{self.type}_logits"].update(
                    {
                        "target_{}_output_{}".format(
                            self.target_class_labels[w], self.target_class_labels[w]
                        ): logits[w, self.target_classes[w]]
                        .mean()
                        .tolist()
                    }
                )
            if self.verbose > 2:
                data_log[f"{self.base_class_labels}_{self.type}_logits"].update(
                    {
                        "target_{}_output_{}".format(
                            self.target_class_labels[w], self.config.class_list[c]
                        ): logits[w, c].tolist()
                        for c in range(len(self.config.class_list))
                    }
                )
                data_log[f"{self.base_class_labels}_{self.type}_probs"].update(
                    {
                        "target_{}_output_{}".format(
                            self.target_class_labels[w], self.config.class_list[c]
                        ): probs[w, c].tolist()
                        for c in range(len(self.config.class_list))
                    }
                )
        if return_log:
            return data_log
        else:
            self.logging_fn(step, data_log, {})

    def verbose_log(
        self,
        step,
        logits,
        probs,
        losses,
        transformed_input,
        post_proc,
        post_proc_alpha_collapsed,
        orig_logits,
        final=False,
    ):
        if self.verbose < 1:
            return
        data_log, file_log = (

            self.step_log(step, logits, probs, losses, return_log=True),
            {},
        )

        labels_and_probs = get_labels(
            self.target_classes, self.config.class_list, probs)  # if self.type in ['prototype', 'saliency'] else self.target_class_labels

        file_log[f"{self.base_class_labels}_{self.type}"] = [
            LeapFile(
                "IMAGE",
                f"{self.file_path}{step}_{p}_{self.base_class_labels_str + self.target_class_labels[p]}.png",
                pp,
                caption=labels_and_probs[p],
                mode=self.config.mode,
            )
            for p, pp in enumerate(post_proc)
        ]

        if self.verbose > 1:
            file_log[f"{self.base_class_labels}_{self.type}_transformed"] = [
                LeapFile(
                    "IMAGE",
                    f"{self.file_path}{step}_{p}_{self.base_class_labels_str + self.target_class_labels[p]}_transformed.png",
                    pp,
                    caption=labels_and_probs[p],
                    mode=self.config.mode,
                )
                for p, pp in enumerate(transformed_input)
            ]
            if self.config.use_alpha:
                file_log[f"{self.base_class_labels}_{self.type}_alpha"] = [
                    LeapFile(
                        "IMAGE",
                        f"{self.file_path}{step}_{p}_{self.base_class_labels_str + self.target_class_labels[p]}_alpha.png",
                        pp[-1:] if self.config.mode == "pt" else pp[:, :, -1:],
                        caption=labels_and_probs[p],
                        mode=self.config.mode,
                    )
                    for p, pp in enumerate(post_proc)
                ]

                file_log[f"{self.base_class_labels}_{self.type}_a"] = [
                    LeapFile(
                        "IMAGE",
                        f"{self.file_path}{step}_{p}_{self.base_class_labels_str + self.target_class_labels[p]}_a.png",
                        pp,
                        caption=labels_and_probs[p],
                        mode=self.config.mode,
                    )
                    for p, pp in enumerate(post_proc)
                ]

                file_log[f"{self.base_class_labels}_{self.type}_collapsed"] = [
                    LeapFile(
                        "IMAGE",
                        f"{self.file_path}{step}_{p}_{self.base_class_labels_str + self.target_class_labels[p]}_collapsed.png",
                        pp,
                        caption=labels_and_probs[p],
                        mode=self.config.mode,
                    )
                    for p, pp in enumerate(post_proc_alpha_collapsed)
                ]

        if final and self.type != "baseline":
            if self.type == "prototype":
                table = np.empty(
                    (len(self.config.class_list) * len(self.target_classes), 10),
                    dtype=object,
                )
                table[:, 0] = self.config.class_list * len(self.target_classes)
                table[:, 1] = np.array(self.target_class_labels).repeat(
                    len(self.config.class_list)
                )
                table[:, 2] = logits.flatten()
                table[:, 3] = probs.flatten()
                table[:, 4] = calc_entanglement(orig_logits, logits).flatten()
                table[:, 5] = orig_logits.flatten()
                table[:, 6] = list(range(len(self.config.class_list))) * len(
                    self.target_classes
                )
                table[:, 7] = np.array(self.config.target_class_ix).repeat(
                    len(self.config.class_list)
                )
                self.columns = [
                    "output_class",
                    "target_class",
                    "logits",
                    "probs",
                    "entanglement",
                    "orig_logits",
                    "output_ix",
                    "target_ix",
                    "input",
                    "input",
                ]

                for it, t in enumerate(self.target_classes):
                    for row in table:
                        if row[-4] == row[-3] == t[0]:
                            row[-2] = file_log[f"{self.base_class_labels}_{self.type}"][
                                it
                            ].to_wandb_image()
                            row[-1] = file_log[f"{self.base_class_labels}_{self.type}"][
                                it
                            ]
                self.table = table

            if self.type == "isolation":
                for it, t in enumerate(self.target_classes):
                    for row in self.table:
                        if row[-4] == t[0] and row[-3] == self.base_classes[0]:
                            if row[-1] is None:
                                row[-2] = file_log[
                                    f"{self.base_class_labels}_{self.type}"
                                ][it].to_wandb_image()
                                row[-1] = file_log[
                                    f"{self.base_class_labels}_{self.type}"
                                ][it]

            if self.type == "saliency":
                table = np.empty((len(self.target_classes), 5), dtype=object)
                table[:, 0] = self.target_class_labels
                table[:, 1] = logits[self.target_mask.astype(bool)].flatten()
                table[:, 2] = probs[self.target_mask.astype(bool)].flatten()
                table[:, 3] = [
                    im.to_wandb_image()
                    for im in file_log[f"{self.base_class_labels}_{self.type}"]
                ]
                table[:, 4] = [
                    im for im in file_log[f"{self.base_class_labels}_{self.type}"]
                ]
                self.columns = ["output_class",
                                "logits", "probs", "input", "input"]
                self.table = table

            data_log["wandb_table"] = LeapData(
                "WANDB_TABLE",
                path=self.file_path,
                columns=self.columns[:-1],
                rows=self.table[:, :-1],
            )
            if self.type == "prototype":
                data_log["prototype_entanglement"] = LeapData(
                    "VEGA",
                    path=self.file_path,
                    columns=self.columns[:-2],
                    rows=self.table[:, :-2],
                    vega_preset="prototype_entanglement",
                )

        self.logging_fn(step, data_log, file_log)

    def get_table(self):
        if self.type in ["prototype", "isolation"]:
            tab = np.delete(self.table, [5, 6, 7, 8], axis=1)
            for row in tab:
                if row[-1] is not None:
                    row[-1] = row[-1].path
            col = [self.columns[c] for c in [0, 1, 2, 3, 4, 9]]
            return col, tab
        elif self.type == "saliency":
            tab = np.delete(self.table, 3, axis=1)
            col = [self.columns[c] for c in [0, 1, 2, 4]]
            for row in tab:
                if row[-1] is not None:
                    row[-1] = row[-1].path
            return col, tab
        else:
            return None, None

    def finish(self):
        if self.leap_logging:
            self.leap_run.finish()
        if self.config.wandb_api_key is not None:
            wandb.finish()


class LeapFile:
    def __init__(
        self, content_type, path=None, pixels=None, caption="", priority=1, mode="pt"
    ):
        self.content_type = content_type
        self.path = path or ""
        self.name = path.split("/")[-1].split(".")[0]
        self.pixels = pixels
        self.caption = caption
        self.priority = priority
        self.mode = mode

        if self.content_type == "IMAGE":

            if pixels.shape[0] == 1:
                pixels = pixels[0]
            elif pixels.shape[-1] == 1:
                pixels = np.squeeze(pixels, axis=-1)
            else:
                if self.mode == 'pt':
                    pixels = pixels.transpose(1, 2, 0)

            if pixels.shape[-1] == 4:
                pixels[:, :, :-1] = normalise(pixels[:, :, :-1])
                pixels[:, :, -1:] = normalise(pixels[:, :, -1:])
            else:
                pixels = normalise(pixels)
            self.pixels = pixels

            img = Image.fromarray((self.pixels * 255).astype("uint8"))
            img.save(self.path)

    def to_wandb_image(self):
        if self.content_type == "IMAGE":
            return wandb.Image(self.pixels, caption=self.caption)
        else:
            return None


class LeapData:
    def __init__(
        self,
        content_type,
        path=None,
        columns=None,
        rows=None,
        vega_preset=None,
        priority=3,
    ):
        self.content_type = content_type
        self.columns = columns
        self.rows = rows.tolist()
        self.path = path or ""
        if content_type == "VEGA":
            self.vega_values = [{c: r[i]
                                 for i, c in enumerate(columns)} for r in rows]
            with open("{}.json".format(self.path + vega_preset), "w") as file:
                json.dump(self.vega_values, file)
        if vega_preset == "prototype_entanglement":
            self.data = entanglement_chart(self.vega_values)
        if vega_preset == "entanglement_matrix":
            self.data = entanglement_matrix(self.vega_values)
        if vega_preset == "entanglement_graph":
            self.data = entanglement_graph(self.vega_values)
        self.priority = priority

    def to_wandb(self):
        if self.content_type == "VEGA":
            return None
        if self.columns is not None and self.rows is not None:
            return wandb.Table(
                columns=self.columns, data=[list(row) for row in self.rows]
            )
        else:
            return None

    def to_st(self, entity, project):
        # st = StreamTable(f"{entity}/{project}/stream_table")  # st.log(self.table_dict)
        return
