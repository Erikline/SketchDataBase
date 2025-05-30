# 🖼️ 项目名称：草图图片检索系统

## 🏗️ 项目架构

- **Flask**：用于构建后端API，处理用户请求并提供动态网页内容。
- **MVC架构**：使用Model-View-Controller（模型-视图-控制器）架构来分离业务逻辑、用户界面和数据存储。

## 📦 项目环境与依赖库

安装项目所需的依赖库，请使用以下命令：

```bash
pip install flask
pip install werkzeug
pip install pillow
pip install torch
pip install numpy
pip install scipy
pip install matplotlib
pip install tqdm
```

这些命令会安装项目所需的所有基本库。为了确保所有依赖都能正确安装，您也可以创建一个`requirements.txt`文件，并执行以下命令：

```bash
pip install -r requirements.txt
```

其中，`requirements.txt`的内容如下：

```
flask
werkzeug
pillow
torch
numpy
scipy
matplotlib
tqdm
```

## 📁 文件描述

### 数据集

- **data**：
  - `Partial-SketchyRawData`：草图数据集
- **examples_digit/sketch**：提供测试用的样例数据集

### 项目目录

#### handwriting_sketchdb: 基于草图方式检索数据库的图像项目
- **models**：
  - `sketchy_model_resnet34.pth`：训练好的ResNet-34模型权重文件，用于图像检索。
- **sketchy_database**：
  - `photos`：真实照片数据集。
  - `sketches`：草图数据集。
  - `pair.txt`：记录真实照片与草图之间对应关系的文件，包含重新命名的配对信息。
- **static**：静态资源文件夹。
- **templates**：
  - `index.html`：前端页面模板，用户交互界面。
- **uploads**：用于缓存上传的草图和照片。

#### 训练与测试脚本

- **train_sketchdb_model.py**：用于训练ResNet-34模型，使用Triplet Loss和SGD优化器进行训练，适用于草图和照片的匹配。

## 🚀 如何运行项目

### 1. 安装依赖

首先，确保您已安装所有依赖库。可以通过以下命令来安装：

```bash
pip install -r requirements.txt
```

### 2. 训练模型

在训练模型之前，确保您的数据集已经准备好，并且将其放在合适的文件夹中。然后，使用以下命令训练模型：

```bash
python train_sketchdb_model.py
```

### 3. 启动应用

在项目根目录下，运行Flask应用以启动前端和后端服务：

```bash
python app.py
```

然后，您可以在浏览器中访问 `http://localhost:5000` 或 `http://localhost:8000`（请根据您的 `app.py` 中实际配置的端口确认），以便与手写数字识别系统或草图图片检索系统进行交互。

### 4. 上传与测试

- **草图检索**：上传草图图像，系统将从照片数据库中基于余弦相似度检索最相似的图像。

## ✨ 项目特色与优势

- **高效的图像识别**：使用ResNet-34模型进行深度学习训练，确保高效且准确的图像识别。
- **草图检索**：基于草图与照片的匹配，使用Triplet Loss优化模型，提供更精准的图像检索结果。
- **早停机制**：在训练时引入早停机制，避免过拟合，确保模型的泛化能力。

## 📄 许可证 (License)

本项目根据 **[MIT 许可证](https://opensource.org/licenses/MIT)** 条款进行许可。

这意味着您被授予了非常广泛的权利，可以自由地使用、复制、修改、合并、出版、分发、再许可 (sublicense) 和/或销售本软件的副本，并且可以允许获得软件副本的人也这样做，但须遵守以下条件：

*   上述版权声明和本许可声明必须包含在本软件的所有副本或主要部分中。

本软件按“原样”提供，不作任何形式的保证，无论是明示的还是默示的，包括但不限于对适销性、特定用途适用性和非侵权性的保证。在任何情况下，作者或版权持有人均不对任何索赔、损害或其他责任承担任何责任，无论是在合同诉讼、侵权行为还是其他方面，即使是因本软件或本软件的使用或其他处理方式而引起的或与之相关的。

有关完整的许可条款，请参阅项目根目录下的 [`LICENSE`](./LICENSE) 文件。
