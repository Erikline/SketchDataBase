import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import torch.utils.model_zoo as model_zoo
from tqdm import tqdm
import math
import random

# 预训练模型 URL
model_urls = {
    'resnet18': 'https://download.pytorch.org/models/resnet18-5c106cde.pth',
    'resnet34': 'https://download.pytorch.org/models/resnet34-333f7ec4.pth',
    'resnet50': 'https://download.pytorch.org/models/resnet50-19c8e357.pth',
    'resnet101': 'https://download.pytorch.org/models/resnet101-5d3b4d8f.pth',
    'resnet152': 'https://download.pytorch.org/models/resnet152-b121ed2d.pth',
}


# 3x3 卷积
def conv3x3(in_planes, out_planes, stride=1):
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride, padding=1, bias=False)


# 基础残差块
class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super(BasicBlock, self).__init__()
        self.conv1 = conv3x3(inplanes, planes, stride)
        self.bn1 = nn.BatchNorm2d(planes)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = conv3x3(planes, planes)
        self.bn2 = nn.BatchNorm2d(planes)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out


# 瓶颈残差块
class Bottleneck(nn.Module):
    expansion = 4

    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super(Bottleneck, self).__init__()
        self.conv1 = nn.Conv2d(inplanes, planes, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)
        self.conv3 = nn.Conv2d(planes, planes * 4, kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm2d(planes * 4)
        self.relu = nn.ReLU(inplace=True)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out


# ResNet 主类
class ResNet(nn.Module):
    def __init__(self, block, layers, embed_dim=128, num_classes=1000):
        self.inplanes = 64
        super(ResNet, self).__init__()
        self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.layer1 = self._make_layer(block, 64, layers[0])
        self.layer2 = self._make_layer(block, 128, layers[1], stride=2)
        self.layer3 = self._make_layer(block, 256, layers[2], stride=2)
        self.layer4 = self._make_layer(block, 512, layers[3], stride=2)
        self.avgpool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Linear(512 * block.expansion, embed_dim)  # 输出 embed_dim 维嵌入向量

        # 初始化权重
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()

    def _make_layer(self, block, planes, blocks, stride=1):
        downsample = None
        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.inplanes, planes * block.expansion, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(planes * block.expansion),
            )

        layers = []
        layers.append(block(self.inplanes, planes, stride, downsample))
        self.inplanes = planes * block.expansion
        for i in range(1, blocks):
            layers.append(block(self.inplanes, planes))

        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avgpool(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)  # 输出 embed_dim 维嵌入向量
        return x


# ResNet-50 模型定义
def resnet50(pretrained=False, **kwargs):
    model = ResNet(Bottleneck, [3, 4, 6, 3], **kwargs)
    if pretrained:
        pretrained_dict = model_zoo.load_url(model_urls['resnet50'])
        model_dict = model.state_dict()

        pretrained_dict = {k: v for k, v in pretrained_dict.items() if
                           k in model_dict and v.size() == model_dict[k].size()}

        model_dict.update(pretrained_dict)
        model.load_state_dict(model_dict)
    return model


# ResNet-34 模型定义
def resnet34(pretrained=False, **kwargs):
    model = ResNet(BasicBlock, [3, 4, 6, 3], **kwargs)
    if pretrained:
        pretrained_dict = model_zoo.load_url(model_urls['resnet34'])
        model_dict = model.state_dict()

        pretrained_dict = {k: v for k, v in pretrained_dict.items() if
                           k in model_dict and v.size() == model_dict[k].size()}

        model_dict.update(pretrained_dict)
        model.load_state_dict(model_dict)
    return model


# 自定义数据集类
class SketchyDataset(Dataset):
    def __init__(self, pairs_file, transform=None):
        self.pairs = []
        self.labels = []
        # 设置基础路径
        self.base_photo_path = '/home/maline/AMI/MNIST_SYSYEM/handwriting_sketchdb/'  # 照片基础路径
        self.base_sketch_path = '/home/maline/AMI/MNIST_SYSYEM/handwriting_sketchdb/'  # 草图基础路径
        with open(pairs_file, 'r') as f:
            for line in f:
                photo_path, sketch_path, label = line.strip().split('\t')

                # 修正路径
                corrected_photo_path = self._correct_path(photo_path, 'photos')
                corrected_sketch_path = self._correct_path(sketch_path, 'sketches')

                self.pairs.append((corrected_photo_path, corrected_sketch_path))
                self.labels.append(int(label))

        self.transform = transform

    def _correct_path(self, path, folder_type):
        """根据路径类型（照片或草图）修正路径"""
        if folder_type == 'photos':
            base_path = self.base_photo_path
        else:
            base_path = self.base_sketch_path

        # 如果路径是相对路径，自动加上基础路径
        if not path.startswith('/'):
            path = os.path.join(base_path, path)
        return path

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        photo_path, sketch_path = self.pairs[idx]
        label = self.labels[idx]

        # 检查文件是否存在
        photo = Image.open(photo_path).convert('RGB')
        sketch = Image.open(sketch_path).convert('RGB')

        if self.transform:
            photo = self.transform(photo)
            sketch = self.transform(sketch)

        return sketch, photo, label


# 图像预处理
transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

# 创建数据集和数据加载器
pairs_file = r'/home/maline/AMI/MNIST_SYSYEM/handwriting_sketchdb/pairs.txt'
dataset = SketchyDataset(pairs_file, transform=transform)
train_loader = DataLoader(dataset, batch_size=32, shuffle=True)

# 初始化模型、损失函数和优化器
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = resnet34(pretrained=True, embed_dim=5).to(device)  # 输出 5 维嵌入向量
criterion = nn.TripletMarginLoss(margin=1.0, p=2)  # 使用三元组损失
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 训练循环
num_epochs = 100
for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    progress_bar = tqdm(train_loader, desc=f'Epoch {epoch + 1}/{num_epochs}')
    for sketches, photos, labels in progress_bar:
        sketches, photos, labels = sketches.to(device), photos.to(device), labels.to(device)
        optimizer.zero_grad()

        # 获取嵌入向量
        sketch_embed = model(sketches)
        photo_embed = model(photos)

        # 构建三元组: (anchor, positive, negative)
        # 选择负样本
        negative_indices = []
        for i in range(len(labels)):
            # 选择与当前样本标签不同的样本作为负样本
            negative_idx = random.choice([j for j in range(len(labels)) if labels[j] != labels[i]])
            negative_indices.append(negative_idx)

        # 生成三元组
        anchor = photo_embed
        positive = photo_embed
        negative = sketch_embed[negative_indices]  # 选择对应的负样本

        loss = criterion(anchor, positive, negative)  # 计算三元组损失
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        progress_bar.set_postfix(loss=running_loss / len(train_loader))

    print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {running_loss / len(train_loader):.4f}')
