import requests


def get_opf_layers_and_formats(pecha_id):
    meta_url = f"https://raw.githubusercontent.com/OpenPecha/{pecha_id}/master/{pecha_id}.opf/meta.yml"
    content = requests.get(meta_url).content.decode()
    layer_names = []
    formats = [".epub", ".docx", ".md", ".txt"]
    for layer_name in content.split("layers:")[-1].split("-"):
        cleaned_layer_name = layer_name.strip()
        if not cleaned_layer_name:
            continue
        layer_names.append(cleaned_layer_name)
    return layer_names, formats


if __name__ == "__main__":
    layers = get_opf_layers("P000780")
    print(layers)
