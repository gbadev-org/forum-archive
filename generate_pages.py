import dateparser
import json
from mako.template import Template
from pathlib import Path
from tqdm import tqdm
import re

templates = {}
templates["base"] = Template(filename="templates/base.html")


def build_webpage(template_name, output_path, title, obj):
    if template_name not in templates:
        templates[template_name] = Template(filename=f"templates/{template_name}.html")
    data = templates["base"].render(
        title=title, contents=templates[template_name].render(**obj)
    )
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as fp:
        fp.write(data)


tqdm.write("Loading...")
data = {}
with open("output.json", "r") as fp:
    data = json.load(fp)

tqdm.write("Generating index page...")
data["category_ids_sorted"] = list(
    sorted(data["categories"].keys(), key=lambda x: data["categories"][x]["name"])
)
build_webpage("index", "site/index.html", "gbadev.org forum archive", data)

threads_to_category = {}

tqdm.write("Generating category pages...")
for category_id in tqdm(data["category_ids_sorted"]):
    data["category_id"] = category_id
    data["category"] = data["categories"][category_id]
    data["thread_ids_sorted"] = list(
        sorted(
            filter(
                lambda x: data["threads"][x]["category_id"] == int(category_id),
                data["threads"].keys(),
            ),
            key=lambda x: -int(x),
        )
    )
    for i in data["thread_ids_sorted"]:
        threads_to_category[i] = category_id
    build_webpage(
        "category",
        f"site/category/{category_id}.html",
        f"{data['categories'][category_id]['name']} - gbadev.org forum archive",
        data,
    )

tqdm.write("Generating thread pages...")
for thread_id in tqdm(data["threads"].keys()):
    thread = data["threads"][thread_id]
    category_id = threads_to_category[thread_id]
    data["category_id"] = category_id
    data["category"] = data["categories"][data["category_id"]]
    data["thread_id"] = thread_id
    data["thread"] = thread
    data["post_ids_sorted"] = list(
        map(
            lambda x: str(x[1]),
            sorted(thread["posts"].items(), key=lambda x: int(x[0])),
        )
    )
    build_webpage(
        "thread",
        f"site/thread/{category_id}/{thread_id}.html",
        f"{thread['name']} - gbadev.org forum archive",
        data,
    )
