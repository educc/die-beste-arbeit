import json

FILENAME = "./application.json"


class ConfigApp:

    def __init__(self):
        self.first_navigation_page = None
        self.out_dir_navigation_pages = None
        self.out_dir_job_pages = None

    def load_from_json(self, json_filename):
        with open(json_filename, "r") as f:
            data = json.load(f)
            self.first_navigation_page = data.get("firstNavigationPage", None)

            if "outDir" in data:
                self.out_dir_navigation_pages = data["outDir"].get("navigationPages", None)
                self.out_dir_job_pages = data["outDir"].get("jobPages", None)


configApp = ConfigApp()
configApp.load_from_json(FILENAME)

