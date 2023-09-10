from tqdm import tqdm
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms
from torchvision.transforms import ToTensor
from net.model import NeuralNetwork as N
from net.model2 import NeuralNetwork2 as N2
#
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--batch_size', type=int, default=64, help='train batch size')
parser.add_argument('--epoch', type=int, default=5, help='the number of epochs to train for')
parser.add_argument('--lr', type=float, default=1e-3, help='learning rate')  # [0.001, 0.0005, 0.0001]
parser.add_argument('--project_name', type=str, default='DA', help='project name on wandb')
parser.add_argument('--task_name', type=str, default='first', help='experiment name on wandb')
parser.add_argument('--entity', type=str, default='', help='entity on wandb')
parser.add_argument('--model', type=str, default='1', help='model')


opt = parser.parse_args()
print(opt)

# init wandb settings
def run(opt):
    #
    #
    # 
    # update
    
    
    # Download training data from open datasets.
    training_data = datasets.FashionMNIST(
        root="data",
        train=True,
        download=True,
        transform=ToTensor(),
    )

    # Download test data from open datasets.
    test_data = datasets.FashionMNIST(
        root="data",
        train=False,
        download=True,
        transform=ToTensor(),
    )

    # Create data loaders.
    train_dataloader = DataLoader(training_data, batch_size=#)
    test_dataloader = DataLoader(test_data, batch_size=#cfg[''])

    # Get cpu or gpu device for training.
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using {device} device")

    if opt.model =='1':
        model = N().to(device)
    elif opt.model =='2':
        model = N2().to(device)
    elif opt.model =='resnet':
         # 이미지 전처리 및 변환
        transform = transforms.Compose([
        transforms.Resize((224, 224)),  # ResNet 모델은 일반적으로 큰 이미지를 처리하기 때문에 크기 조정
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),  # ImageNet 데이터셋의 평균과 표준편차
        ])
        training_data = datasets.FashionMNIST(
        root="data",
        train=True,
        download=True,
        transform=transform,  # 이전 코드에서 사용한 transform 대신 새로 정의한 transform을 사용
        )

        test_data = datasets.FashionMNIST(
            root="data",
            train=False,
            download=True,
            transform=transform,  # 이전 코드에서 사용한 transform 대신 새로 정의한 transform을 사용
        )
        model = models.resnet18(pretrained=True)
        # ResNet 모델의 첫 번째 합성곱 레이어를 1개의 입력 채널을 처리하도록 변경
        model.conv1 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
        
        num_ftrs = model.fc.in_features
        # 마지막 Fully Connected 레이어를 FashionMNIST에 맞게 변경
        model.fc = nn.Linear(num_ftrs, 10)
        model=model.to(device)
    

    print(model)
    

    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=#cfg[''])


    def train(dataloader, model, loss_fn, optimizer, epoch):
        size = len(dataloader.dataset)
        model.train()
        total_loss = 0
        for batch, (X, y) in enumerate(tqdm(dataloader)):
            X, y = X.to(device), y.to(device)

            # Compute prediction error
            pred = model(X)
            loss = loss_fn(pred, y)
            total_loss += loss.item()

            # Backpropagation
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if batch % 100 == 0:
                loss, current = loss.item(), batch * len(X)
                print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")
        # wandb.log 함수를 통해 metric 값들을 logging
        # log 함수의 파라미터는 항상 dictionary 형태
        # 기본적으로 wandb 차트의 x축은 자동적으로 step을 지정
        wandb.log({"train_loss": total_loss / len(dataloader)}, step=epoch)
        # metrics={'bleu1':bleu1,'rouge':rouge}
        # wandb.log(metrics, step=epoch)
        # wandb.alert(title='제목', text='내용')

    def test(dataloader, model, loss_fn, epoch, log_images=False, idx=0):
        size = len(dataloader.dataset)
        num_batches = len(dataloader)
        model.eval()
        test_loss, correct = 0, 0
        with torch.no_grad():
            for i,(X, y) in enumerate(tqdm(dataloader)):
                X, y = X.to(device), y.to(device)
                pred = model(X)
                test_loss += loss_fn(pred, y).item()
                _, predicted = torch.max(pred.data, 1)
                correct += (pred.argmax(1) == y).type(torch.float).sum().item()
                # Log one batch of images to the dashboard, always same batch_idx.
                if i==idx and log_images:
                    log_image_table(X, predicted, y, pred.softmax(dim=1))
        test_loss /= num_batches
        correct /= size
        print(f"Test Error: \n Accuracy: {(100*correct):>0.1f}%, Avg loss: {test_loss:>8f} \n")
        wandb.log({"test_loss": test_loss, "test_acc": correct}, step=epoch)

    def log_image_table(images, predicted, labels, probs):
        "Log a wandb.Table with (img, pred, target, scores)"
        # 🐝 Create a wandb Table to log images, labels and predictions to
        table = wandb.Table(columns=["image", "pred", "target"]+[f"score_{i}" for i in range(10)])
        for img, pred, targ, prob in zip(images.to("cpu"), predicted.to("cpu"), labels.to("cpu"), probs.to("cpu")):
            table.add_data(wandb.Image(img[0].numpy()*255), pred, targ, *prob.numpy())
        wandb.log({"predictions_table":table}, commit=False)
        
    epochs = #cfg['']
    for t in range(epochs):
        print(f"Epoch {t+1}\n-------------------------------")
        train(train_dataloader, model, loss_fn, optimizer, t)
        test(test_dataloader, model, loss_fn, t,log_images=(t==(epochs-1)))
    print("Done!")

    torch.save(model.state_dict(), "model.pth")
    print("Saved PyTorch Model State to model.pth")
    if opt.model =='1':
        model = N()
        model.load_state_dict(torch.load("model.pth"))
    elif opt.model =='2':
        model = N2()
        model.load_state_dict(torch.load("model.pth"))
    
    classes = [
        "T-shirt/top",
        "Trouser",
        "Pullover",
        "Dress",
        "Coat",
        "Sandal",
        "Shirt",
        "Sneaker",
        "Bag",
        "Ankle boot",
    ]

    model.eval()
    x, y = test_data[0][0], test_data[0][1]
    with torch.no_grad():
        pred = model(x)
        predicted, actual = classes[pred[0].argmax(0)], classes[y]
        print(f'Predicted: "{predicted}", Actual: "{actual}"')
        

def main():
    run(opt)


if __name__ == "__main__":
    main()