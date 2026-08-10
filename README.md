# Multimodal-Pathological-Gait-Dataset
A Multimodal Dataset for Pathological Gait Classification Using Consumer-Grade Devices

paper link 
dataset link

---

## Abstract

Instrumented gait analysis (IGA) utilizes motion data to diagnose gait abnormalities, evaluate treatment efficacy, and inform rehabilitation strategies; however, its resource-, time-, and labor-intensive nature motivates the development of scalable, low-cost consumer-device solutions for remote and routine gait assessment.

Thus, we aim to automatically classify **six gait classes** — five pathological patterns (*paraparesis, hemiparesis, Duchenne, Trendelenburg, and foot drop*) and *normal gait* — using a multimodal setup of commercial sensors.

In cooperation with **three physiotherapy training centers**, we collected recordings of these six classes from recruited physiotherapy trainees, capturing:
* Smartphone inertial sensor data
* Smartwatch inertial sensor data
* Acoustic step signals
* Markerless pose estimates extracted from video

We evaluated both unimodal and multimodal approaches and performed late fusion via majority voting. Unimodal classification achieved accuracies up to **77%** (with pose landmark data yielding the best performance), while combining multiple modalities increased overall accuracy to **89.4%**. 

We provide meaningful baseline results on the dataset, which we make public as a robust reference for future comparisons and methodological developments.

---

## Dataset Overview

### Gait Classes (6 Total)
1. **Normal Gait** (Control)
2. **Paraparesis**
3. **Hemiparesis**
4. **Duchenne Gait**
5. **Trendelenburg Gait**
6. **Foot Drop**

### Sensor Modalities
| Modality | Device Type | Data Recorded |
| :--- | :--- | :--- |
| **Smartphone IMU** | Consumer Smartphone | Accelerometer & Gyroscope streams |
| **Smartwatch IMU** | Consumer Smartwatch | Wrist motion / Accelerometer data |
| **Acoustic Signals** | Standard Microphone | Audio recordings of footfall step sounds |
| **Markerless Video** | RGB Camera | Extracted body pose landmarks / coordinates |

---

## Benchmark Baseline Results

| Approach | Setup / Method | Accuracy |
| :--- | :--- | :---: |
| **Unimodal (Best)** | Markerless Pose Landmarks | **77.0%** |
| **Multimodal Fusion** | Late Fusion (Majority Voting) | **89.4%** |

---

## Data Structure

```text
├── data/
