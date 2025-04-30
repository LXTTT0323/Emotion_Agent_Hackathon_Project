# README: LSTM Model Training for Emotion Detection (WESAD Dataset)

## Project Overview
This project builds and trains an LSTM model to predict emotional states (Baseline, Stress, Amusement) based on heart rate variability (HRV) features extracted from the WESAD dataset.

- **Dataset**: WESAD (Wearable Stress and Affect Detection)
- **Features Used**: HRV SDNN and its time-lagged features (lag1, lag2)
- **Labels**:
  - 0 = Baseline
  - 1 = Stress
  - 2 = Amusement

## Files
- `train/modeltraining.ipynb`: Jupyter Notebook containing code for data preparation, model training, and evaluation.
- `predict.py`: Inference file to load the trained model and perform predictions on new HRV data.
- `requirements.txt`: List of Python packages required.

## Setup
1. Install required packages:
    ```bash
    pip install -r requirements.txt
    ```

2. Ensure the WESAD dataset files are available, specifically:
    - HRV extracted data (`HeartRateVariabilitySDNN.csv`) for prediction.
    - Raw `.pkl` or `.csv` files if retraining from scratch.

3. Model File:
    - Place `lstm_emotion_model.h5` in the correct directory as referenced in the code.

## Training Workflow (`modeltraining.ipynb`)
1. **Data Preparation**
    - Load HRV data(download from WESAD official website).
    - Generate lagged features: `HRV_SDNN_lag1`, `HRV_SDNN_lag2`.
    - Handle missing values by filling them with zero.
2. **Sliding Window Generation**
    - Using a window size of 5.
    - Each input to LSTM has shape `(window_size, 3 features)`.
3. **Model Architecture**
    - LSTM layer(s)
    - Dense output layer with softmax activation (for multi-class classification)
4. **Training**
    - Optimizer: Adam
    - Loss function: Sparse Categorical Crossentropy
    - Metrics: Accuracy
5. **Model Saving**
    - Save the trained model as `lstm_emotion_model.h5`.

## Prediction Workflow (`predict.py`)
1. Load new HRV data.
2. Preprocess and create sliding windows.
3. Load trained LSTM model.
4. Predict emotional states.
5. Output predictions.
