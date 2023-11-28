from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


class HerdCompositionGraphGenerator:
    @staticmethod
    def generate_herd_composition_graph(indir: Path, outdir: Path, infile_name_substr: str,
                                        outfile_name: str = 'herd_composition.png',
                                        common_prefix: str = 'AnimalManager.daily_updates.') -> None:
        # Load Data
        csv_files = list(indir.glob(f'*{infile_name_substr}*.csv'))
        if not csv_files:
            raise ValueError(f'No files found in {indir} with substring {infile_name_substr}')
        latest_csv = max(csv_files, key=lambda path: path.stat().st_ctime)
        print(f'Using {latest_csv} to generate graph')

        df = pd.read_csv(latest_csv)

        # Remove Common Prefix
        df.columns = [col.replace(common_prefix, '') for col in df.columns]

        # Plot
        colors = sns.color_palette('hls', 7)
        plt.figure(figsize=(10, 6))
        plt.plot(df['sim_day'], df['num_animals'], label='Total Animals', color=colors[0])
        plt.plot(df['sim_day'], df['num_calves'], label='Calves', color=colors[1], linestyle='--')
        plt.plot(df['sim_day'], df['num_heiferIs'], label='HeiferIs', color=colors[2], linestyle='--')
        plt.plot(df['sim_day'], df['num_heiferIIs'], label='HeiferIIs', color=colors[3])
        plt.plot(df['sim_day'], df['num_heiferIIIs'], label='HeiferIIIs', color=colors[4], linestyle='--')
        plt.plot(df['sim_day'], df['num_lactating_cows'], label='Lactating Cows', color=colors[5])
        plt.plot(df['sim_day'], df['num_dry_cows'], label='Dry Cows', color=colors[6], linestyle='--')

        # Labels and Legend
        plt.xlabel('Simulation Day')
        plt.ylabel('Number of Animals')
        plt.title('Herd Composition Over Time')
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1))

        # Save the Graph
        plt.savefig(outdir / outfile_name, dpi=300, bbox_inches='tight')
        plt.close()

    @staticmethod
    def generate_cow_parity_composition_graph(indir: Path, outdir: Path, infile_name_substr: str,
                                              outfile_name: str = 'cow_parity_composition.png',
                                              common_prefix: str = 'AnimalManager.daily_updates.') -> None:
        # Load Data
        csv_files = list(indir.glob(f'*{infile_name_substr}*.csv'))
        if not csv_files:
            raise ValueError(f'No files found in {indir} with substring {infile_name_substr}')
        latest_csv = max(csv_files, key=lambda path: path.stat().st_ctime)
        print(f'Using {latest_csv} to generate graph')

        df = pd.read_csv(latest_csv)

        # Remove Common Prefix
        df.columns = [col.replace(common_prefix, '') for col in df.columns]

        # Plot
        colors = sns.color_palette('hls', 7)
        plt.figure(figsize=(10, 6))
        plt.plot(df['sim_day'], df['num_cows'], label='Total Cows', color=colors[0])
        plt.plot(df['sim_day'], df['num_cow_parity_1'], label='Parity-1 Cows', color=colors[1])
        plt.plot(df['sim_day'], df['num_cow_parity_2'], label='Parity-2 Cows', color=colors[2])
        plt.plot(df['sim_day'], df['num_cow_parity_3'], label='Parity-3 Cows', color=colors[3])
        plt.plot(df['sim_day'], df['num_cow_parity_3+'], label='Parity-3+ Cows', color=colors[4])

        # Labels and Legend
        plt.xlabel('Simulation Day')
        plt.ylabel('Number of Cows')
        plt.title('Cow Parity Composition Over Time')
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1))

        # Save the Graph
        plt.savefig(outdir / outfile_name, dpi=300, bbox_inches='tight')
        plt.close()
