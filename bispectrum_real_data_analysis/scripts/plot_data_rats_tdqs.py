import pandas as pd
import plotly.express as px
import os
from plotly.subplots import make_subplots
from bispectrum_real_data_analysis.scripts.utils import standardize_array
from loguru import logger
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

"""
This function plots the data from the csv file generated by the script generate_bispectrum_of_data.py.
To filter one channel, double click one of the lines in the legend. then, select the other corresponding line (if you
clicked in the amplitude, select the phase line and vice versa). All the 16 channels are plotted in the same figure.
The plot in the first row is the amplitude and the plot in the second row is the phase.
"""

if __name__ == "__main__":

    # Select which data to plot

    rat_number: int = 1

    group_number: int = 5

    plot_mean: bool = True

    BASE_PATH = os.getcwd() + f"/bispectrum_real_data_analysis/scripts/rats_analysis/group{group_number}rat{rat_number}"  

    for data_to_process in ("train", "test"):

        hosa_to_plot = ("spectrum", "bispectrum", "trispectrum", "hosa")[3]

        prefix_rat: str = f"rato-{rat_number}-grupo-{group_number}-{data_to_process}"

        experiment_date = "27-04-2023"

        logger.info(f"Plotting {hosa_to_plot} data from {prefix_rat} processed in {experiment_date}.")

        files_to_plot = [
            f"{BASE_PATH}/{f}" for f in os.listdir(BASE_PATH) 
            if os.path.isfile(os.path.join(BASE_PATH, f)) 
            and f.startswith(hosa_to_plot)
            and prefix_rat in f
            and f.endswith(f"{experiment_date}.csv")
        ]   

        standardize = False

        for file in files_to_plot:
            logger.info(f"Plotting {file.split('/')[-1]}")
            df = pd.read_csv(file, delimiter=',', encoding="utf8")

            band_to_plot = (4, 60)

            df = df[(df.iloc[:, 0]>=band_to_plot[0])&(df.iloc[:, 0]<=band_to_plot[1])]

            spectrum_colum_amp = [column for column in df.columns if column.startswith("tds_amp")]
            bispectrum_colum_amp = [column for column in df.columns if column.startswith("tdbs_amp")]
            trispectrum_colum_amp = [column for column in df.columns if column.startswith("tdts_amp")]
            tetraspectrum_colum_amp = [column for column in df.columns if column.startswith("tdqs_amp")]

            amplitudes_df = df.loc[:, spectrum_colum_amp + bispectrum_colum_amp + trispectrum_colum_amp + tetraspectrum_colum_amp]
            if standardize:
                amplitudes_df = amplitudes_df.apply(lambda x: standardize_array(x, scale_to_unit=True))

            spectrum_colum_phase = [column for column in df.columns if column.startswith("tds_phase")]
            bispectrum_colum_phase = [column for column in df.columns if column.startswith("tdbs_phase")]
            trispectrum_colum_phase = [column for column in df.columns if column.startswith("tdts_phase")]
            tetraspectrum_colum_phase = [column for column in df.columns if column.startswith("tdqs_phase")]

            phases_df = df.loc[:, spectrum_colum_phase + bispectrum_colum_phase + trispectrum_colum_phase + tetraspectrum_colum_phase]

            title = file.split('/')[-1].split('.')[0]

            fig = make_subplots(rows=4, cols=1, subplot_titles=('Spectrum',  'Bispectrum', 'Trispectrum', 'Quadrispectrum'))

            fig.update_layout(
                font_family="Courier New",
                font_color="blue",
                title_font_family="Times New Roman",
                title_font_color="black",
                legend_title_font_color="green",
                title=f"Amplitude - {title}"
            )

            amplitudes = px.line(amplitudes_df, x=df.iloc[:, 0], y=amplitudes_df.columns)

            figplt = plt.figure(figsize=(14,10))
            figplt.tight_layout(pad=0.8, h_pad=100.0)

            ax1 = figplt.add_subplot(411)
            ax2 = figplt.add_subplot(412)
            ax3 = figplt.add_subplot(413)
            ax4 = figplt.add_subplot(414)

            ymin_spectrum = float('inf')
            ymax_spectrum = float('-inf')

            ymin_bispectrum = float('inf')
            ymax_bispectrum = float('-inf')

            ymin_trispectrum = float('inf')
            ymax_trispectrum = float('-inf')

            ymin_tetraspectrum = float('inf')
            ymax_tetraspectrum = float('-inf')


            if plot_mean:
                tds = np.zeros(len(amplitudes['data'][0].y))
                tdbs = tds.copy()
                tdts = tds.copy()
                tdqs = tds.copy()
                frequency = amplitudes['data'][0].x
                for amplitude in amplitudes['data']:
                    if amplitude.legendgroup.startswith("tds"):
                        tds += amplitude.y
                    elif amplitude.legendgroup.startswith("tdbs"):
                        tdbs += amplitude.y
                    elif amplitude.legendgroup.startswith("tdts"):
                        tdts += amplitude.y
                    elif amplitude.legendgroup.startswith("tdqs"):
                        tdqs += amplitude.y
                

                fig.add_trace(go.Scatter(x=frequency, y=tds/5, name="avg_spectrum"), row=1, col=1)
                fig.add_trace(go.Scatter(x=frequency, y=tdbs/5, name="avg_bispectrum"), row=2, col=1)
                fig.add_trace(go.Scatter(x=frequency, y=tdts/5, name="avg_trispectrum"), row=3, col=1)
                fig.add_trace(go.Scatter(x=frequency, y=tdqs/5, name="avg_quadrispectrum"), row=4, col=1)
                fig.show()
                continue
            else:

                for amplitude in amplitudes['data']:
                    i = 1*(amplitude.legendgroup.startswith("tds")) + \
                    2 * (amplitude.legendgroup.startswith("tdbs")) + \
                    3 * (amplitude.legendgroup.startswith("tdts")) + \
                    4 * (amplitude.legendgroup.startswith("tdqs"))

                    fig.add_trace(amplitude, row=i, col=1)
                
                    ax = (ax1, ax2, ax3, ax4)[i-1]

                    if i == 1:
                        ymin_spectrum = min(ymin_spectrum, np.min(amplitude.y))
                        ymax_spectrum = max(ymax_spectrum, np.max(amplitude.y))
                    elif i == 2:
                        ymin_bispectrum = min(ymin_bispectrum, np.min(amplitude.y))
                        ymax_bispectrum = max(ymax_bispectrum, np.max(amplitude.y))
                    elif i == 3:
                        ymin_trispectrum = min(ymin_trispectrum, np.min(amplitude.y))
                        ymax_trispectrum = max(ymax_trispectrum, np.max(amplitude.y))
                    elif i == 4:
                        ymin_tetraspectrum = min(ymin_tetraspectrum, np.min(amplitude.y))
                        ymax_tetraspectrum = max(ymax_tetraspectrum, np.max(amplitude.y))

                    ax.plot(amplitude.x, amplitude.y, label=amplitude.legendgroup)
                fig.show()

            continue
            fontsize = 25


            # ax1.set_xlabel("Frequency [Hz]", fontsize=fontsize)
            ax1.set_ylabel('Spectrum', fontsize=fontsize)
            t = ax1.yaxis.get_offset_text()
            t.set_size(16)

            # ax2.set_xlabel("Frequency [Hz]", fontsize=fontsize)
            ax2.set_ylabel('Bispectrum', fontsize=fontsize)
            t = ax2.yaxis.get_offset_text()
            t.set_size(16)

            ax3.set_ylabel('Trispectrum', fontsize=fontsize)
            t = ax3.yaxis.get_offset_text()
            t.set_size(16)

            ax4.set_xlabel("Frequency [Hz]", fontsize=fontsize)
            ax4.set_ylabel('Tetraspectrum', fontsize=fontsize)
            t = ax4.yaxis.get_offset_text()
            t.set_size(16)

            ax1.set_xticks(np.sort(np.append(np.linspace(band_to_plot[0], band_to_plot[1], 4), [53.71])), fontsize=fontsize)
            ax1.set_yticks(np.linspace(ymin_spectrum, ymax_spectrum, 5), fontsize=fontsize)
            ax1.set_xlim([band_to_plot[0], band_to_plot[1]])

            ax2.set_xticks(np.sort(np.append(np.linspace(band_to_plot[0], band_to_plot[1], 4), [53.71])), fontsize=fontsize)
            ax2.set_yticks(np.linspace(ymin_bispectrum, ymax_bispectrum, 5), fontsize=fontsize)
            ax2.set_xlim([band_to_plot[0], band_to_plot[1]])

            ax3.set_xticks(np.sort(np.append(np.linspace(band_to_plot[0], band_to_plot[1], 4), [53.71])), fontsize=fontsize)
            ax3.set_yticks(np.linspace(ymin_trispectrum, ymax_trispectrum, 5), fontsize=fontsize)
            ax3.set_xlim([band_to_plot[0], band_to_plot[1]])

            ax4.set_xticks(np.sort(np.append(np.linspace(band_to_plot[0], band_to_plot[1], 4), [53.71])), fontsize=fontsize)
            ax4.set_yticks(np.linspace(ymin_tetraspectrum, ymax_tetraspectrum, 5), fontsize=fontsize)
            ax4.set_xlim([band_to_plot[0], band_to_plot[1]])

            plt.savefig(
                f"{title}.eps",
                format="eps",
                bbox_inches='tight', 
                dpi=150
            )
            
            plt.show()
            
            del ax1, ax2, ax3, ax4


            # fig = make_subplots(rows=3, cols=1)

            # fig.update_layout(
            #     font_family="Courier New",
            #     font_color="blue",
            #     title_font_family="Times New Roman",
            #     title_font_color="black",
            #     legend_title_font_color="green",
            #     title=f"Phase - {title}"
            # )

            # phases = px.line(phases_df, x=df.iloc[:, 0], y=phases_df.columns)

            # for phase in phases['data']:
            #     i = 1*(phase.legendgroup.startswith("tds")) + \
            #     2 * (phase.legendgroup.startswith("tdbs")) + \
            #     3 * (phase.legendgroup.startswith("tdts"))
            #     fig.add_trace(phase, row=i, col=1)
            
            # fig.show()
            
    logger.success("Done!")
