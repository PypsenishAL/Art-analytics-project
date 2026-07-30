# Visual Similarity and Artwork Prices

This repository contains a research project about artwork pricing at auction. The main question is whether the visual similarity of a new artwork to previously sold works affects its final price.

The project combines auction metadata, computer vision and econometric analysis. Instead of describing an artwork only through its author, date and estimate, the analysis also uses information extracted directly from the image.

## Project idea

Artwork images are converted into numerical embeddings with the pretrained **SigLIP** model. The embeddings are reduced with PCA and grouped into visual clusters with K-Means. Several interpretable image features are also calculated, including brightness, saturation, contrast, entropy, colorfulness, warmth and aspect ratio.

Based on these features, the project measures:

- how typical an artwork is within its visual cluster;
- how close it is to expensive works from the same visual group;
- the prices of its nearest visual neighbours;
- its similarity to expensive and lower-priced artworks.

These variables are then used in hedonic regressions and machine-learning models for artwork price prediction.

## Data

The research is based on auction lots collected from major auction houses, mainly **Christie's** and **Phillips**, covering several years of sales. The repository also contains an experimental Sotheby's parser used during the data-collection stage.

The original data was cleaned by removing duplicates, records without the required price or image information, and three-dimensional objects that could not be compared correctly using the selected image-based approach.

The complete image dataset is too large to store in this repository, so the notebooks use prepared files and local or Google Colab paths that may need to be changed before running.

## Main steps

1. Collect and clean auction data.
2. Download and validate artwork images.
3. Extract SigLIP image embeddings.
4. Reduce embedding dimensionality with PCA.
5. Create visual clusters with K-Means.
6. Calculate visual and similarity-based features.
7. Estimate hedonic regressions and train a LightGBM price model.

## Main findings

The results show that visual information contains a meaningful pricing signal, although the artist's identity and market position remain the strongest factors.

Visual cluster membership is related to price, and artworks located near expensive visual references tend to receive higher valuations. The analysis also suggests that the market does not simply reward works that are maximally typical. In many cases, buyers appear to value originality within a recognizable visual style. The size and direction of this effect differ across auction platforms and price segments.

Adding visual and similarity features also improves the predictive performance of the price model compared with specifications based only on structural auction variables.

## Repository structure

- `Art_analytics_project (1).ipynb` - image preprocessing, embedding extraction, PCA, clustering and visual feature engineering.
- `PriceForecast_HypothesisTesting.ipynb` - LightGBM price modelling, model evaluation and hypothesis-testing pipeline.
- `main_sothebys_parser.py` - Selenium parser for collecting Sotheby's auction lots.
- `data/` - sample auction image folders.
- `embeddings_data/` - files related to prepared image embeddings.

## Technologies

Python, pandas, NumPy, scikit-learn, PyTorch, Hugging Face Transformers, SigLIP, LightGBM, Selenium, SciPy, Matplotlib and Seaborn.

## Running the project

Clone the repository and install the main dependencies:

```bash
git clone https://github.com/PypsenishAL/Art-analytics-project.git
cd Art-analytics-project

pip install pandas numpy scipy scikit-learn lightgbm torch torchvision \
    transformers pillow h5py selenium fake-useragent tqdm matplotlib seaborn
```

The notebooks were mainly developed in Google Colab. Before running them, update the paths to the datasets, images and saved embeddings for your environment. GPU access is recommended for generating SigLIP embeddings, but the remaining analysis can be run on CPU.

## Project status

This is a research and educational project. The repository contains the main data-processing and modelling code, while some paths and intermediate files still reflect the original experimental environment.
