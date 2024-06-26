from flask import Flask, request, jsonify
import io
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image



app = Flask(__name__)



class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(NeuralNet, self).__init__()
        self.l1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.l2 = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        out = self.l1(x)
        out = self.relu(out)
        out = self.l2(out)
        return out
    

input_size = 784  #  28x28
hidden_size = 100
num_classes = 10
model = NeuralNet(input_size, hidden_size, num_classes)

PATH = "mnist_ffn.pth"
model.load_state_dict(torch.load(PATH))
model.eval()


def transform_image(image_bytes):
    #model was trained on greyscale images of size 28x28
    transform = transforms.Compose([transforms.Grayscale(num_output_channels=1),
                                    transforms.Resize((28,28)),
                                    transforms.ToTensor(),
                                    transforms.Normalize((.1307,),(0.3081,))])
    
    image = Image.open(io.BytesIO(image_bytes))
                       
    return transform(image).unsqueeze(0)  # model was trained on batches.  So here the tensor must have a dimension for batch size, with only one image in our batch



def get_prediction(image_tensor):
    images = image_tensor.reshape(-1, 28*28)
    outputs = model(images)

    # max returns  (value, index)
    _, predicted = torch.max(outputs.data, 1)
    return predicted



allowed_extensions = {'png', 'jpg', 'jpeg'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in allowed_extensions
   


@app.route('/predict',methods=['POST'])
def predict():

    if request.method == 'POST':
        file = request.files.get('file')
        if file is None or file.filename == "":
            return jsonify({'error': 'no file'})
        if not allowed_file(file.filename):
            return jsonify({'error': 'format not supported'})

        
        #try:                  #  try / except pair not very good error handeling, but good enoguh for now
        img_bytes = file.read()
        tensor = transform_image(img_bytes)
        prediction = get_prediction(tensor)
        data = {'prediction': prediction.item(), 'class_name': str(prediction.item())}
        return jsonify(data)

        #except:
         #   return jsonify({'error': 'error during prediction'})

