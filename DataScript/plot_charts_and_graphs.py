#################### IMPORTS ####################
# AS
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import nibabel as nib  # For neuroimaging data
import plotly.express as px

# FROM
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from PIL import Image
from scipy.stats import skew
from tqdm import tqdm

#################### FUNCTIONS ####################

# This function will plot a histogram
def plot_histogram(data, x, xlabel, title, ylabel, pltlibrary='px'):
    if pltlibrary == 'px':
        fig = px.histogram(data, x=x, title=title, labels={data.columns[0]: xlabel})
        #px.histogram(ref_df, x='label')
        fig.show()
    elif pltlibrary == 'sns':
        plt.figure(figsize=(12, 6))
        sns.histplot(data, kde=True)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.show()

# This function will plot a scatter plot
def plot_scatter(data, x, y, title, xlabel, ylabel, colour, pltlibrary='px'):
    if pltlibrary == 'px':
        fig = px.scatter(data, x=x, y=y, title=title, color=colour, labels={x: xlabel, y: ylabel})
        fig.show()
    elif pltlibrary == 'sns':
        plt.figure(figsize=(12, 6))
        sns.scatterplot(x, y)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.show()

# This function will plot a bar chart
def plot_bar_chart(data, title, xlabel, ylabel, pltlibrary='px'):
    if pltlibrary == 'px':
        fig = px.bar(data, x=data.index, y=data.values, title=title, labels={data.columns[0]: xlabel, data.columns[1]: ylabel})
        fig.show()

    elif pltlibrary == 'sns':
        plt.figure(figsize=(12, 6))
        sns.barplot(data.index, data.values)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.show()

# This function will plot a box plot
def plot_box_plot(data, x, y, title, xlabel, ylabel, pltlibrary='px'):
    if pltlibrary == 'px':
        fig = px.box(data, y=y, x=x, title=title, labels={data.columns[0]: xlabel, data.columns[1]: ylabel})
        fig.show()
    elif pltlibrary == 'sns':
        plt.figure(figsize=(12, 6))
        sns.boxplot(x=x, y=y, data=data)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.show()
    # px.box(image_stats, y='mean', x='label')

# This function will plot a line chart
def plot_line_chart(data, title, xlabel, ylabel, pltlibrary='px'):
    if pltlibrary == 'px':
        fig = px.line(data, x=data.index, y=data.values, title=title, labels={data.columns[0]: xlabel, data.columns[1]: ylabel})
        fig.show()
    elif pltlibrary == 'sns':
        plt.figure(figsize=(12, 6))
        sns.lineplot(data.index, data.values)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.show()

# This function will plot a pie chart
def plot_pie_chart(data, title, pltlibrary='px'):
    if pltlibrary == 'px':
        fig = px.pie(data, names=data.index, values=data.values, title=title)
        fig.show()
    elif pltlibrary == 'sns':
        plt.figure(figsize=(12, 6))
        plt.pie(data, labels=data.index, autopct='%1.1f%%')
        plt.title(title)
        plt.show()

# This function will plot a heatmap
def plot_heatmap(data, title, xlabel, ylabel, pltlibrary='px'):
    if pltlibrary == 'px':
        fig = px.imshow(data, title=title, labels={data.columns[0]: xlabel, data.columns[1]: ylabel})
        fig.show()
    elif pltlibrary == 'sns':
        plt.figure(figsize=(12, 6))
        sns.heatmap(data, annot=True, cmap='coolwarm')
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.show()

# This function will plot a 3D scatter plot
def plot_3d_scatter(data, x, y, z, title, xlabel, ylabel, zlabel, colour, pltlibrary='px'):
    if pltlibrary == 'px':
        fig = px.scatter_3d(data, x=x, y=y, z=z, color=colour, title=title, labels={x: xlabel, y: ylabel, z: zlabel})
        #px.scatter_3d(sampled_image_stats, x='mean', y='std', z='skew', color='label', title='3D Scatter Plot of Image Statistics')
        fig.show()
    elif pltlibrary == 'sns':
        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(x, y, z)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_zlabel(zlabel)
        plt.title(title)
        plt.show()
        

# This function will plot a 3D line chart
def plot_3d_line_chart(data, x, y, z, title, xlabel, ylabel, zlabel, colour, pltlibrary='px'):
    if pltlibrary == 'px':
        fig = px.line_3d(data, x=x, y=y, z=z, color=colour, title=title, labels={x: xlabel, y: ylabel, z: zlabel})
        fig.show()
    elif pltlibrary == 'sns':
        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(x, y, z)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_zlabel(zlabel)
        plt.title(title)
        plt.show()

# This function will plot a 3D surface plot
def plot_3d_surface(data, x, y, z, title, xlabel, ylabel, zlabel, colour, pltlibrary='px'):
    if pltlibrary == 'px':
        fig = px.surface(data, x=x, y=y, z=z, color=colour, title=title, labels={x: xlabel, y: ylabel, z: zlabel})
        fig.show()
    elif pltlibrary == 'sns':
        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(x, y, z)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_zlabel(zlabel)
        plt.title(title)
        plt.show()

# This function will plot a 3D mesh plot
def plot_3d_mesh(data, x, y, z, title, xlabel, ylabel, zlabel, colour, pltlibrary='px'):
    if pltlibrary == 'px':
        fig = px.mesh(data, x=x, y=y, z=z, color=colour, title=title, labels={x: xlabel, y: ylabel, z: zlabel})
        fig.show()
    elif pltlibrary == 'sns':
        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_trisurf(x, y, z, cmap='viridis', edgecolor='none')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_zlabel(zlabel)
        plt.title(title)
        plt.show()

# This function will plot a 3D contour plot
def plot_3d_contour(data, x, y, z, title, xlabel, ylabel, zlabel, colour, pltlibrary='px'):
    if pltlibrary == 'px':
        fig = px.contour(data, x=x, y=y, z=z, color=colour, title=title, labels={x: xlabel, y: ylabel, z: zlabel})
        fig.show()
    elif pltlibrary == 'sns':
        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.contour3D(x, y, z, 50, cmap='viridis')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_zlabel(zlabel)
        plt.title(title)
        plt.show()