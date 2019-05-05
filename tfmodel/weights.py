import h5py

## Helper functions to handle Caffe's H5 Shape
def h5_group_to_list(group):
    return [group[i].value for i in list(group)]


def restructure_weights_conv(weights, layer):
    w = h5_group_to_list(weights[layer])
    w[0] = np.swapaxes(w[0], 0, 3)
    w[0] = np.swapaxes(w[0], 1, 2)
    return w


def restructure_weights_bn(weights, layer):
    bn_w = h5_group_to_list(weights[layer])
    sc = 'sc' + layer[2:]
    sc_w = h5_group_to_list(weights[sc])
    return bn_w[:2] + sc_w


def restructure_weights_flip0(weights, layer):
    w = h5_group_to_list(weights[layer])
    w[0] = np.swapaxes(w[0], 0, 1)
    return w

def load_weights(model, weights_path):
    weights = h5py.File(weights_path, 'r')
    w = weights['data']
    unloaded = []
    for layer in model.layers:
        if layer.name in list(weights['data']):
            print(f"loading {layer.name}")
            if layer.name[:4] == 'conv' and "conv" in layer.name: # Load Normal Conv Weights
                these_weights = restructure_weights_conv(w, layer.name)
                layer.set_weights(these_weights)
            elif layer.name[:2] == 'bn' and "conv" in layer.name:
                these_weights = restructure_weights_bn(w, layer.name)
                layer.set_weights(these_weights)
            elif layer.name == "fc7":
                layer.set_weights(h5_group_to_list(w[layer.name]))
            elif layer.name in ["fc6", "cls_score", "bbox_pred_3d"]:
                these_weights = restructure_weights_flip0(w, layer.name)
                layer.set_weights(these_weights)
            else:
                unloaded.append(layer.name)
            print(f"loaded {layer.name}")
        else: # No data from Deng weights...
            unloaded.append(layer.name)
    return model

