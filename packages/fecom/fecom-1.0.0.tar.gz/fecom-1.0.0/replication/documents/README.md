# RQ3 Issue Log
This file provides a detailed list of issues faced.
The list of issues faced are grouped into 4 categories:
1. [Energy Measurement](#energy-measurement)
2. [Patching](#patching)
3. [Execution Environment](#execution-environment)
4. [Framework Design and Implementation](#framework-design-and-implementation)

Within each category, the issues are further grouped into subcategories.
## Energy Measurement
This category details issues that hinder effective energy
measurement.

| Subcategory                       | Issue                      | Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|-----------------------------------|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Instrumentation Challenges        | Instrumentation overhead   | Instrumented code has additional computing instructions that may account for overhead and therefore may impact the performance and energy consumption of the code. To address this challenge, we implement machine stability and temperature stability checks. If these checks pass, the console should show the following: <pre>

    ### Experiment Settings ###
    "wait_per_stable_check_loop_s": 20,
    "tolerance": 0,
    "measurement_interval_s": 0.5,
    "check_last_n_points": 20,
    "cpu_max_temp": 55,
    "gpu_max_temp": 40,
    "cpu_temperature_interval_s": 1
    Perf started
    Nvidia-smi started
    Please wait 120 seconds to see if the machine is in a stable state
    Stats after 120 seconds:
    CPU stdev/mean ratio: 0.28 (current) vs 0.03 (config) vs 0.03 (config + tolerance)
    RAM stdev/mean ratio: 0.148 (current) vs 0.03 (config) vs 0.03 (config + tolerance)
    GPU stdev/mean ratio: 0.005 (current) vs 0.01 (config) vs 0.01 (config + tolerance)
    If the current ratios are significantly larger than the config ones, there might be an excess number of background processes running.
</pre>                                                                                                                                                                                                                                      |
| Instrumentation Challenges        | Noise in measurement       | Background processes running on the machine during energy measurement introduce noise and overheads, affecting the accuracy of measured energy. To mitigate this, we ensure only necessary background processes are run during energy consumption experiments. We also measure the net energy consumption by subtracting the energy of the stable baseline from the total energy consumed during measurements.                                                                                                                                                                   |
| Hardware Variability              | Hardware configuration     | According to [Cao et. al](https://aclanthology.org/2020.sustainlp-1.19), different hardware configurations can lead to variations in energy consumption values for the same project. To mitigate this, we ensure all our energy observations come from the same machine, a Ubuntu 22.04 machine equipped with an Intel(R) Xeon(R) Gold 5317 CPU, 24 logical cores, and a base frequency of 3.00 GHz. The GPU used is an NVIDIA GeForce RTX 3070 Ti with 8GB GDDR6X memory.                                                                                                       |
| Hardware Variability              | Calibration Issues         | To account for hardware variations, energy measurement tools require calibration. While the energy observations were collected from the same machine, additional calibration processes were implemented. These included the calculating of stable-state energy consumption, maximum allowed temperature thresholds, and wait times. These values are specific to the used hardware configuration, and are reused across experiments on the same machine.                                                                                                                         |
| Hardware Variability              | GPU Usage                  | Errors in environment configuration may occur such that TensorFlow may not be utilizing the GPU, leading to incorrect and inconsistent energy data collection.<br>One way to reduce the probability of such errors occurring is to read the [official TensorFlow documentation](https://www.tensorflow.org/install/pip) and verify the GPU setup before initiating the experiments, using the command:<pre>python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"</pre>A successful installation of TensorFlow should return a list of GPU devices. |
| Granularity of energy attribution | Precision limits           | Intel RAPL updates its energy counters every [~1 ms](https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/advisory-guidance/running-average-power-limit-energy-reporting.html). Thus, it is not possible to collect readings at intervals smaller than 1 ms. This limitation is also observed on the Perf tool, which generates error `Error: switch 'I' expects a numerical value` when executing the command `perf stat -I 0.9 -e power/energy-pkg/,power/energy-ram/`                                                              |
| Granularity of energy attribution | Precision overhead balance | The precision of energy consumption data can be improved when observed at a higher frequency. However, higher observation frequencies may also introduce computation overheads, resulting in additional noise to the observed energy data.                                                                                                                                                                                                                                                                                                                                       |

## Patching
The issues and challenges listed below discuss
the considerations related to static instrumentation of code.

| Subcategory      | Issue                  | Details                                                                                                                                                                                                                                                                                                                                                   |
|------------------|------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Patch Generation | Correctness of Patches | Each identified patch location (TensorFlow APIs in our case) must be correctly patched to record the correct energy consumption of the API and not introduce new syntactic or semantic issues. To ensure correctness, manual validation was performed on the patched scripts. The manual validation step was done for which more information can be found in the [validation](https://anonymous.4open.science/r/FECoM/replication/validation/README.md) folder of this repo. |
| Patch Generation | Patch coverage         | Each patch location must be identified correctly to avoid missing code that is supposed to be patched and measured. To ensure correctness, manual validation was performed on the patched scripts. The manual validation step was done for which more information can be found in the [validation](https://anonymous.4open.science/r/FECoM/replication/validation/README.md) folder of this repo.                                                                            |

## Execution Environment
This category deals with issues related to execution environment, which may hinder effective measurement of consumed energy.

| Subcategory              | Issue             | Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|--------------------------|-------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Hardware incompatibility | -                 | Compatibility issues arise when certain framework versions are incompatible with hardware or software dependencies on the machine. To mitigate this, we focus only on subject systems that use TensorFlow 2, and referenced the [TensorFlow GPU build configuration table](https://www.tensorflow.org/install/source#gpu) to ensure compliance. In addition, we observe the error logs to confirm that a program execution completes without any errors in the logs.                                                                                                   |
| GPU challenges           | Memory Management | A CUDA runtime error stating that the GPU has ran out of memory occurs when a process cannot be allocated sufficient memory:<pre>std::bad_alloc: CUDA error at: ../include/rmm/mr/device/cuda_memory_resource.hpp:70: cudaErrorMemoryAllocation out of memory</pre>                                                                                                                                                                                                                                                                                                    |
| GPU challenges           | Container Issues  | This issue was encountered while experimenting with the NVIDIA [DeepLearningExamples](https://github.com/NVIDIA/DeepLearningExamples/tree/master) dataset. The examples in the dataset are provided in Docker containers. However, for some examples, the specified version of the TensorFlow container is not compatible with the GPU, resulting in the following error: <pre>WARNING: Detected NVIDIA NVIDIA GeForce RTX 3070 Ti GPU, which is not yet supported in this version of the container<br>ERROR: No supported GPU(s) detected to run this container</pre> |

## Framework Design and Implementation
This category covers the issues that should be considered during the designing process of the framework.

### Framework Extensibility
Ensuring the FECoM framework can handle various programming languages, platforms, and frameworks while working seamlessly across different operating systems and hardware configurations while accommodating future enhancements and additions.