import os
from tkinter import ttk

from thonny import get_workbench, ui_utils
from thonny.config_ui import ConfigurationPage
from thonny.languages import tr
from thonny.tktextext import TextFrame
from thonny.ui_utils import askdirectory, askopenfilename, create_string_var, scrollbar_style


class AssistantGPTConfigPage(ConfigurationPage):
    def __init__(self, master):
        super().__init__(master)

        self.add_checkbox(
            "assistanceGPT.open_assistant_on_errors",
            tr("Open Assistant automatically when program crashes with an exception"),
            row=2,
            columnspan=3,
        )

        self.add_checkbox(
            "assistanceGPT.open_assistant_on_warnings",
            tr("Open Assistant automatically when it has warnings for your code"),
            row=3,
            columnspan=3,
        )

        if get_workbench().get_option("assistanceGPT.use_pylint", "missing") != "missing":
            self.add_checkbox(
                "assistanceGPT.use_pylint",
                tr("Perform selected Pylint checks"),
                row=4,
                columnspan=3,
            )

        if get_workbench().get_option("assistanceGPT.use_mypy", "missing") != "missing":
            self.add_checkbox(
                "assistanceGPT.use_mypy", tr("Perform MyPy checks"), row=5, columnspan=3
            )

        apiKey_label = ttk.Label(self, text=tr("File with API key from the OpenAI platform"))
        apiKey_label.grid(row=6, sticky="nw", pady=(10, 0), columnspan=3)

        self._key_entry = ttk.Combobox(
            self,
            exportselection=False,
            textvariable=get_workbench().get_option("assistanceGPT.gpt_api_key_filepath"),
            values=self._get_api_keyfilepaths(),
        )
        _gpt_api_key_filepath = get_workbench().get_option("assistanceGPT.gpt_api_key_filepath")
        if _gpt_api_key_filepath:
            self._key_entry.set(_gpt_api_key_filepath)
        self._key_entry.state(["!disabled", "readonly"])
        self._key_entry.bind("<<ComboboxSelected>>", self.combobox_selected_key)

        self._key_entry.grid(row=7, column=1, columnspan=2, sticky="nsew")

        self._api_select_button = ttk.Button(
            self,
            text="...",
            width=3,
            command=self._select_api_key,
        )
        self._api_select_button.grid(row=7, column=3, sticky="e", padx=(10, 0))
        self.columnconfigure(1, weight=1)

        system_prompt_label = ttk.Label(self, text=tr("File with system prompt for API response"))
        system_prompt_label.grid(row=8, sticky="nw", pady=(10, 0), column=1, columnspan=3)

        reset_system_prompt = ui_utils.create_action_label(
            self,
            tr("Set system prompt to default"),
            self.set_default_system_prompt,
        )
        reset_system_prompt.grid(row=10, column=2, sticky="se")

        self._system_prompt_entry = ttk.Combobox(
            self,
            exportselection=False,
            textvariable=get_workbench().get_option("assistanceGPT.system_prompt_filepath"),
            values=self._get_system_prompt_filepaths(),
        )
        _system_prompt_filepath = get_workbench().get_option("assistanceGPT.system_prompt_filepath")
        if _system_prompt_filepath:
            self._system_prompt_entry.set(_system_prompt_filepath)
        self._system_prompt_entry.state(["!disabled", "readonly"])
        self._system_prompt_entry.bind("<<ComboboxSelected>>", self.combobox_selected_system_prompt)

        self._system_prompt_entry.grid(row=9, column=1, columnspan=2, sticky="nsew")

        self._system_prompt_select_button = ttk.Button(
            self,
            text="...",
            width=3,
            command=self._select_system_prompt,
        )
        self._system_prompt_select_button.grid(row=9, column=3, sticky="e", padx=(10, 0))
        extra_text = tr(
            """The model 'gpt-4o-mini-2024-07-18' is used with the following parameters:
- temperature = 0.7 (Creativity of responses)
- top_p = 0.7 (Probability control)
- max_tokens = 150 (Limits the maximum response length)
- frequency_penalty = 0.6 (Reduces repetitions in responses)"""
        )
        extra_label = ttk.Label(self, text=extra_text)
        extra_label.grid(row=11, columnspan=3, pady=10, sticky="w")
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

    def set_default_system_prompt(self, event=None):
        create_string_var(get_workbench().set_option("assistanceGPT.system_prompt", ""))
        create_string_var(get_workbench().set_option("assistanceGPT.system_prompt_filepath", ""))
        create_string_var(get_workbench().set_option("assistanceGPT.system_prompt_filename", ""))
        self._system_prompt_entry.set("")
        self._system_prompt_entry["values"] = []

        get_workbench().get_view("AssistantViewGPT").update_assistant_gpt_viewer()

    def combobox_selected_key(self, event):
        _gpt_filepath = event.widget.get()
        _gpt_directory, _gpt_filename = os.path.split(_gpt_filepath)

        get_workbench().set_option("assistanceGPT.gpt_api_key_filename", _gpt_filename)
        get_workbench().set_option(
            "assistanceGPT.gpt_api_key_filepath", os.path.join(_gpt_directory, _gpt_filename)
        )
        get_workbench().set_option(
            "assistanceGPT.gpt_api_key", self._read_file_to_string(_gpt_filepath)
        )

        get_workbench().get_view("AssistantViewGPT").update_assistant_gpt_viewer()

    def combobox_selected_system_prompt(self, event):
        _system_prompt_filepath = event.widget.get()
        _system_prompt_directory, _system_prompt_filename = os.path.split(_system_prompt_filepath)

        get_workbench().set_option("assistanceGPT.system_prompt_filename", _system_prompt_filename)
        get_workbench().set_option(
            "assistanceGPT.system_prompt_filepath",
            os.path.join(_system_prompt_directory, _system_prompt_filename),
        )
        get_workbench().set_option(
            "assistanceGPT.system_prompt", self._read_file_to_string(_system_prompt_filepath)
        )

        get_workbench().get_view("AssistantViewGPT").update_assistant_gpt_viewer()

    def _get_api_keyfilepaths(self):
        result = []
        _gpt_filepath = get_workbench().get_option("assistanceGPT.gpt_api_key_filepath")
        if _gpt_filepath and _gpt_filepath != "" and os.path.exists(_gpt_filepath):
            directory = os.path.dirname(_gpt_filepath)
            for file in os.listdir(directory):
                if (
                    os.path.isfile(os.path.join(directory, file))
                    and os.path.splitext(file)[1] == ".key"
                ):
                    result.append(directory + "/" + file)

        print(result)
        print(get_workbench().get_option("assistanceGPT.gpt_api_key_filepath"))
        return result

    def _get_system_prompt_filepaths(self):
        result = []
        _system_prompt_filepath = get_workbench().get_option("assistanceGPT.system_prompt_filepath")
        if (
            _system_prompt_filepath
            and _system_prompt_filepath != ""
            and os.path.exists(_system_prompt_filepath)
        ):
            directory = os.path.dirname(_system_prompt_filepath)
            for file in os.listdir(directory):
                if (
                    os.path.isfile(os.path.join(directory, file))
                    and os.path.splitext(file)[1] == ".txt"
                ):
                    result.append(directory + "/" + file)

        print(result)
        print(get_workbench().get_option("assistanceGPT.system_prompt_filepath"))
        return result

    def _select_api_key(self):
        # TODO: get dir of current interpreter
        options = {"parent": self.winfo_toplevel()}
        options["filetypes"] = [
            (tr("GPT Key"), "*.key"),
            (tr("all files"), ".*"),
        ]

        api_filepath = askopenfilename(**options)
        if not api_filepath:
            return

        if api_filepath:
            _gpt_directory, _gpt_filename = os.path.split(api_filepath)
            _gpt_api_key = self._read_file_to_string(api_filepath)
            create_string_var(get_workbench().set_option("assistanceGPT.gpt_api_key", _gpt_api_key))
            create_string_var(
                get_workbench().set_option("assistanceGPT.gpt_api_key_filepath", api_filepath)
            )
            create_string_var(
                get_workbench().set_option("assistanceGPT.gpt_api_key_filename", _gpt_filename)
            )

            print(
                api_filepath
                + " "
                + _gpt_api_key
                + " => "
                + get_workbench().get_option("assistanceGPT.gpt_api_key")
            )

            self._key_entry.set(api_filepath)
            self._key_entry["values"] = self._get_api_keyfilepaths()

            get_workbench().get_view("AssistantViewGPT").update_assistant_gpt_viewer()
        else:
            self._key_entry.set("")

    def _select_system_prompt(self):
        # TODO: get dir of current interpreter
        options = {"parent": self.winfo_toplevel()}
        options["filetypes"] = [
            (tr("System Prompt"), "*.txt"),
            (tr("all files"), ".*"),
        ]

        system_prompt_filepath = askopenfilename(**options)
        if not system_prompt_filepath:
            return

        if system_prompt_filepath:
            _gpt_directory, _system_prompt_filename = os.path.split(system_prompt_filepath)
            _system_prompt = self._read_file_to_string(system_prompt_filepath)
            create_string_var(
                get_workbench().set_option("assistanceGPT.system_prompt", _system_prompt)
            )
            create_string_var(
                get_workbench().set_option(
                    "assistanceGPT.system_prompt_filepath", system_prompt_filepath
                )
            )
            create_string_var(
                get_workbench().set_option(
                    "assistanceGPT.system_prompt_filename", _system_prompt_filename
                )
            )

            print(
                system_prompt_filepath
                + " "
                + _system_prompt
                + " => "
                + get_workbench().get_option("assistanceGPT.system_prompt")
            )

            self._system_prompt_entry.set(system_prompt_filepath)
            self._system_prompt_entry["values"] = self._get_system_prompt_filepaths()

            get_workbench().get_view("AssistantViewGPT").update_assistant_gpt_viewer()
        else:
            self._system_prompt_entry.set("")

    def _read_file_to_string(self, filepath):
        if filepath:
            with open(filepath, "r") as file:
                return file.read().strip()
        return ""

    def apply(self):
        _system_prompt = self._read_file_to_string(
            get_workbench().get_option("assistanceGPT.system_prompt_filepath")
        )
        create_string_var(get_workbench().set_option("assistanceGPT.system_prompt", _system_prompt))


def load_plugin():
    get_workbench().add_configuration_page(
        "assistantGPT", tr("Assistant") + " GPT", AssistantGPTConfigPage, 80
    )
