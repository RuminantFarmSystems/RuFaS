from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


class HerdCompositionGraphGenerator:
    @staticmethod
    def generate_graph(indir: Path, outdir: Path, infile_name_substr: str,
                       outfile_name: str = 'herd_composition.png',
                       common_prefix: str = 'AnimalManager.daily_updates.') -> None:
        """
        Generate a graph of the herd composition.

        The x-axis should be the time step. The y-axis should be various animal counts:
        total number of animals, number of calves, number of heiferIs, number of heiferIIs,
        number of heiferIIIs, number of dry cows, number of lactating cows.
        """

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
        plt.plot(df['sim_day.values'], df['num_animals.values'], label='Total Animals', color=colors[0])
        plt.plot(df['sim_day.values'], df['num_calves.values'], label='Calves', color=colors[1], linestyle='--')
        plt.plot(df['sim_day.values'], df['num_heiferIs.values'], label='HeiferIs', color=colors[2], linestyle='--')
        plt.plot(df['sim_day.values'], df['num_heiferIIs.values'], label='HeiferIIs', color=colors[3])
        plt.plot(df['sim_day.values'], df['num_heiferIIIs.values'], label='HeiferIIIs', color=colors[4], linestyle='--')
        plt.plot(df['sim_day.values'], df['num_lactating_cows.values'], label='Lactating Cows', color=colors[5])
        plt.plot(df['sim_day.values'], df['num_dry_cows.values'], label='Dry Cows', color=colors[6], linestyle='--')

        # Labels and Legend
        plt.xlabel('Simulation Day')
        plt.ylabel('Number of Animals')
        plt.title('Herd Composition Over Time')
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1))

        # Save the Graph
        plt.savefig(outdir / outfile_name, dpi=300, bbox_inches='tight')
        plt.close()
