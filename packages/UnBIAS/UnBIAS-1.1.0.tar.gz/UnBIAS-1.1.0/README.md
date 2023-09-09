

# UnBIAS - Text Analysis & Debiasing Toolkit

![UnBIAS Logo](path_to_your_logo.png)  <!-- If you have a logo for your project, put its path here -->

`UnBIAS` is a cutting-edge text analysis and debiasing toolkit that aids in assessing and rectifying biases in textual content. Developed with state-of-the-art Transformer models, this toolkit offers:

## Features

- **Bias Classification**: Evaluate textual content and classify its level of bias.
  
- **Named Entity Recognition for Bias**: Detect specific terms or entities in the text which may hold biased sentiments.

- **Text Debiasing**: Process any text and receive a debiased version in return. This ensures the content is neutral concerning gender, race, age groups, and is free from toxic or harmful language.

### Additional Highlights

- **Pre-trained Models**: Uses specialized models from the renowned Hugging Face's Transformers library. These models are especially tailored for bias detection and debiasing tasks.
  
- **Efficient Pipelines**: Designed with intuitive pipelines, making it easier to incorporate into applications or other projects.
  
- **Analytical Tools**: Handy tools available to transform results into structured data for further analysis.

## Installation

To install `UnBIAS`, use pip:

```bash
pip install UnBIAS
```


## Example Usage

```python
# Import necessary class/functions from the package
from unbias import BiasPipeline, results_to_dataframe

# Initialize the pipeline
bias_pipeline = BiasPipeline()

# Input text(s) for analysis
texts = ["I think women are worst at driving"]

# Process the texts
classification_results, ner_results, debiaser_results = bias_pipeline.process(texts)

# Optionally, print the results in a readable format
bias_pipeline.pretty_print(texts, classification_results, ner_results, debiaser_results)

# Or convert results to a dataframe for further analysis
df = results_to_dataframe(texts, classification_results, ner_results, debiaser_results)

```

Visit the [documentation](link_to_your_documentation) for more detailed instructions and examples.  <!-- Replace 'link_to_your_documentation' with actual link if you have one -->

## Contribution

If you wish to contribute to this project, please check out the [contribution guidelines](link_to_contribution_guidelines).  <!-- Replace 'link_to_contribution_guidelines' with actual link if you have one -->

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

---

We hope `UnBIAS` proves useful in your journey to make the digital world a more inclusive and unbiased space. For any queries or feedback, feel free to Shaina Raza at shaina.raza@utoronto.ca

---

