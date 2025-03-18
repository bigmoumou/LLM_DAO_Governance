# LLM DAO Governance

## Overview
LLM DAO Governance is an open-source project designed to analyze and visualize the governance dynamics of a Decentralized Autonomous Organization (DAO). The project includes scripts for crawling governance proposals, analyzing protocol metrics, and tracking treasury assets.

## Features
- **Governance Proposal Analysis**: Extracts and processes KIP (KlimaDAO Improvement Proposals) data.
- **Protocol Metrics Tracking**: Analyzes key governance-related metrics over time.
- **Treasury Asset Monitoring**: Evaluates DAO treasury holdings and trends.
- **Data Visualization**: Provides charts for governance participation and protocol trends.

## Installation
### Prerequisites
- Python 3.8+
- Git

### Setup
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd LLM_DAO_Governance-main
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
### Crawling Governance Data
To fetch governance proposal data:
```bash
python crawl.py
```

### Analyzing Protocol Metrics
To process protocol metrics:
```bash
python protocol_metrics.py
```

### Tracking Treasury Assets
To analyze treasury holdings:
```bash
python treasury_assets.py
```

### Generating Visualizations
Visualized governance participation trends are available in:
```
charts/unique_address_participation.pdf
```

## Data Structure
- **`kip_proposals.csv`**: Summary of all KIP proposals.
- **`kip_proposals_detailed.csv`**: Detailed governance proposal dataset.
- **`protocol_metrics_all.csv`**: Historical protocol metric data.

## Contributing
We welcome contributions! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature/fix.
3. Commit your changes and push to your branch.
4. Submit a pull request.

## License
This project is licensed under the MIT License. See `LICENSE` for details.

## Contact
For questions or support, please open an issue in the repository or reach out to the maintainers.

---
This README provides the necessary steps to install, use, and contribute to the project, ensuring reproducibility for the open-source community.

