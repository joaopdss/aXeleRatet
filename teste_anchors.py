from axelerate.anchor_generator.get_anchors import generate_anchors

config = {}
config["train"] = {}
config["train"]["train_image_folder"] = r'C:\Users\Kafer\Desktop\projetos\Usiminas\bobinas\dataset_vertical\imgs'
config["train"]["train_annot_folder"] = r'C:\Users\Kafer\Desktop\projetos\Usiminas\bobinas\dataset_vertical\anns'
config["model"] = {}
config["model"]["input_size"] = 224
config["model"]["labels"] = ["Bobina"]

anchorList = []
for i in range(0,10):
    anchorList.append(generate_anchors(config, 5))

for item in anchorList:
    print(item)