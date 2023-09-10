import json
import webbrowser
from pathlib import Path
import os


def json_data(file_name):
    with open(file_name, "r") as fp:
        return json.load(fp)


def create_config_file(config, file_name):
    with open(file_name, "w") as wp:
        json.dump(config, wp, indent=4)


def is_valid(value):
    if value:
        if value.strip():
            return True
    return False


def is_empty(value):
    return not is_valid(value)


def get_details(input_dict):
    meta, body, links = input_dict["meta"], input_dict["body"], input_dict["links"]

    # Update Theme
    if meta["theme"] in ["light", "dark", "auto"]:
        print(f"Using {meta['theme']} Theme")
    else:
        print(f"Theme in config is not one of [light, dark, auto]. Setting light theme.")
        meta["theme"] = "light"

    # Setting defaults
    if is_empty(meta["title"]):
        meta["title"] = "Little Link"

    return meta, body, links


def get_services(links: dict, icons: dict, icon_map: dict) -> str:
    # Taking only services with link data
    filtered_links = filter(
        lambda key: is_valid(links[key]["link"]),
        links.keys()
    )
    # Ordering services based on their rank in ASC.
    sorted_links = sorted(
        filtered_links,
        key=lambda key: links[key]["rank"] if links[key]["rank"] else 9999999
    )
    anchor_tags = []
    for _id in sorted_links:
        service = links[_id]
        print(f"Adding {service['service']}.")
        anchor_tags.append(f"""
        <a class="button button-{icon_map[_id]}" href="{service["link"]}" target="_blank" rel="noopener" role="button">
            {icons[_id]}
            {service["text"]}
        </a><br>
        """)

    return "\n".join(anchor_tags)


def get_head(meta, css):
    return f"""
    <head>
        <meta charset="utf-8">
        <title>{meta["title"]}</title>
        <meta name="description" content="{meta["description"]}">
        <meta name="author" content="{meta["name"]}">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <!-- normalize -->
        <style> {css["normalize"]} </style>
        <!-- brands  -->
        <style> {css["brands"]} </style>
        <!-- skeleton  -->
        <style> {css[meta["theme"]]} </style>

        <!-- Favicon  -->
        <link rel="icon" type="image/png" href="data:image/svg+xml,%3Csvg width='24' height='24' viewBox='0 0 24 24' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cg clip-path='url(%23clip0_1432_8697)'%3E%3Cmask id='mask0_1432_8697' style='mask-type:luminance' maskUnits='userSpaceOnUse' x='0' y='0' width='24' height='24'%3E%3Cpath d='M24 0H0V24H24V0Z' fill='white'/%3E%3C/mask%3E%3Cg mask='url(%23mask0_1432_8697)'%3E%3Cpath fill-rule='evenodd' clip-rule='evenodd' d='M0.717708 9.99764C-0.239236 10.9312 -0.239236 12.4449 0.717708 13.3785C1.67465 14.3121 3.22616 14.3121 4.18311 13.3785L12.0335 5.71962L15.2136 8.82223C16.1706 9.75584 17.7221 9.75584 18.679 8.82223C19.636 7.88863 19.636 6.37495 18.679 5.44135L13.8275 0.708111C13.3787 0.270279 12.7992 0.037776 12.2115 0.0106035C11.5097 -0.0539096 10.7849 0.175957 10.2476 0.700204L0.717708 9.99764Z' fill='white'/%3E%3Cpath fill-rule='evenodd' clip-rule='evenodd' d='M23.2823 14.0024C24.2392 13.0688 24.2392 11.5551 23.2823 10.6215C22.3253 9.68786 20.7738 9.68786 19.8169 10.6215L11.9668 18.2801L8.78687 15.1778C7.82992 14.2442 6.27841 14.2442 5.32146 15.1778C4.36452 16.1114 4.36452 17.625 5.32147 18.5587L10.173 23.2919C10.6215 23.7295 11.2007 23.962 11.788 23.9893C12.4899 24.054 13.215 23.8242 13.7524 23.2998L23.2823 14.0024Z' fill='white'/%3E%3C/g%3E%3C/g%3E%3Cdefs%3E%3CclipPath id='clip0_1432_8697'%3E%3Crect width='24' height='24' fill='white'/%3E%3C/clipPath%3E%3C/defs%3E%3C/svg%3E%0A">
    </head>
    """


def get_body(body, services):
    return f"""
    <body>
        <div class="container">
            <div class="row">
                <div class="column" style="margin-top: 10%">
                    <img src="{body["image"]}" class="avatar" alt="">
                    <h1 role="heading">{body["heading"]}</h1>
                    <p>{body["bio"]}</p>
                        {services}
                    <p>{body["footer"]}</p>
                </div>
            </div>
        </div>
    </body>
    """


def save_html(file_name, head, body):
    html = f"""<!DOCTYPE html> \n <html lang="en"> \n {head}  \n {body} \n </html>"""
    with open(file_name, "w") as fp:
        return fp.write(html)


def run(option):
    root_dir = Path(__file__).parent
    assets_file = str(root_dir.joinpath("assets.json"))
    input_config_file = "link_config.json"
    index_html = "index.html"

    assets = json_data(assets_file)
    css, icons, config_template, icon_map = assets["css"], assets["icons"], assets["config"], assets["icon_map"]



    if option["create_config"]:
        create_config_file(config_template, input_config_file)

    if option["generate"]:
        input_dict = json_data(input_config_file)
        meta, body, links = get_details(input_dict)
        services = get_services(links, icons, icon_map)
        head = get_head(meta, css)
        body = get_body(body, services)
        status = save_html(index_html, head, body)
        webbrowser.open(index_html)


if __name__ == '__main__':
    run({'create_config': False, 'generate': False})



