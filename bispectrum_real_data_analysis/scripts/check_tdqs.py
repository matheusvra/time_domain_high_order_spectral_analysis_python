import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from high_order_spectra_analysis.hosa.hosa import Tdhosa
from matplotlib import pyplot as plt
import matplotlib

fontsize = 16
matplotlib.rc("xtick", labelsize=fontsize)
matplotlib.rc("ytick", labelsize=fontsize)
plt.rcParams["figure.figsize"] = [12, 8]
plt.rcParams.update({"font.size": fontsize})

if __name__ == "__main__":
    for norm_before, norm_after, noise in [(False, True, False), (False, True, True)]:
        dtype = np.float32
        time_step = 0.003
        fs = 1 / time_step
        time = np.arange(0, 5, time_step, dtype=dtype)

        freqs = np.array([9, 12, 19, 29, 61], dtype=dtype)
        f1, f2, f3, f4, f5 = tuple(freqs)
        w1, w2, w3, w4, w5 = tuple(2 * np.pi * freqs)
        gains = np.array([1.05, 1.15, 0.8, 0.7, 0.93], dtype=dtype)
        clean_signal = np.cos((w2 + w4) * time)  # add frequency coupling
        clean_signal += np.cos((w1 + w2 + w4) * time)  # add frequency coupling

        for freq, gain in zip(freqs, gains):
            clean_signal += gain * np.cos(2 * np.pi * freq * time)

        signal = clean_signal.astype(dtype) * 1e-5

        # adding noise
        if noise:
            signal += np.random.normal(0, 1 * signal.std(), size=signal.shape).astype(
                dtype
            )

        if norm_before:
            signal = (signal - signal.min()) / (signal.max() - signal.min())
            signal -= signal.mean()

        frequency_array_to_scan = np.arange(0, 70, 0.01, dtype=dtype)

        tdqs_object = Tdhosa(
            frequency_sampling=fs,
            frequency_array=frequency_array_to_scan,
            phase_step=0.5,
        )

        # run tds
        frequency_array, amplitude, phase = tdqs_object.run_tds(signal=signal)

        (
            frequency_array,
            spectrum,
            phase_spectrum,
            bispectrum,
            phase_bispectrum,
            trispectrum,
            phase_trispectrum,
            tetraspectrum,
            phase_tetraspectrum,
        ) = tdqs_object.run_tdqs(signal=signal)

        max_freq_plot = 70

        if norm_after:
            spectrum = (spectrum - spectrum.min()) / (spectrum.max() - spectrum.min())
            bispectrum = (bispectrum - bispectrum.min()) / (
                bispectrum.max() - bispectrum.min()
            )
            trispectrum = (trispectrum - trispectrum.min()) / (
                trispectrum.max() - trispectrum.min()
            )
            tetraspectrum = (tetraspectrum - tetraspectrum.min()) / (
                tetraspectrum.max() - tetraspectrum.min()
            )

        x_ticks: dict = dict(
            zip(
                np.append(freqs, [f2 + f4, f1 + f2 + f4]),
                [f"$f_{i}$" for i in range(1, len(freqs) + 1)]
                + ["$f_2+f_4$", "$f_1+f_2+f_4$"],
            )
        )

        # sort dict by key
        x_ticks = dict(sorted(x_ticks.items(), key=lambda item: item[0]))

        plt.figure(figsize=(20, 15))

        plt.subplot(411)
        plt.plot(
            frequency_array[frequency_array <= max_freq_plot],
            spectrum[frequency_array <= max_freq_plot],
        )
        plt.ylabel("Espectro")
        plt.xticks(list(x_ticks.keys()), list(x_ticks.values()))
        plt.xlim(0, max_freq_plot)

        plt.subplot(412)
        plt.plot(
            frequency_array[frequency_array <= max_freq_plot],
            bispectrum[frequency_array <= max_freq_plot],
        )
        plt.ylabel("Bispectro")
        plt.xticks(list(x_ticks.keys()), x_ticks.values())
        plt.xlim(0, max_freq_plot)

        plt.subplot(413)
        plt.plot(
            frequency_array[frequency_array <= max_freq_plot],
            trispectrum[frequency_array <= max_freq_plot],
        )
        plt.ylabel("Trispectro")
        plt.xticks(list(x_ticks.keys()), x_ticks.values())
        plt.xlim(0, max_freq_plot)

        plt.subplot(414)
        plt.plot(
            frequency_array[frequency_array <= max_freq_plot],
            tetraspectrum[frequency_array <= max_freq_plot],
        )
        plt.ylabel("Quadrispectro")
        plt.xticks(list(x_ticks.keys()), list(x_ticks.keys()))
        plt.xlim(0, max_freq_plot)
        plt.xlabel("Frequência [Hz]")
        plt.savefig(
            f"tdqs_validation{'_clean'*(not noise) + '_noisy'*noise}.jpeg",
            format="jpeg",
        )

        plt.show()

        # break

        # fig = make_subplots(rows=4, cols=1)

        # fig.update_layout(
        #     font_family="Courier New",
        #     font_color="blue",
        #     title_font_family="Times New Roman",
        #     title_font_color="black",
        #     legend_title_font_color="green",
        #     title=f"Normalized before: {norm_before}, Normalized after: {norm_after}"
        # )

        # fig.append_trace(go.Scatter(
        #     x=frequency_array[frequency_array <= max_freq_plot],
        #     y=spectrum[frequency_array <= max_freq_plot],
        #     name="Spectrum",
        # ), row=1, col=1)

        # fig.append_trace(go.Scatter(
        #     x=frequency_array[frequency_array <= max_freq_plot],
        #     y=bispectrum[frequency_array <= max_freq_plot],
        #     name="Bispectrum",
        # ), row=2, col=1)

        # fig.append_trace(go.Scatter(
        #     x=frequency_array[frequency_array <= max_freq_plot],
        #     y=trispectrum[frequency_array <= max_freq_plot],
        #     name="Trispectrum",
        # ), row=3, col=1)

        # fig.append_trace(go.Scatter(
        #     x=frequency_array[frequency_array <= max_freq_plot],
        #     y=tetraspectrum[frequency_array <= max_freq_plot],
        #     name="Tetraspectrum",
        # ), row=4, col=1)

        # fig.show()

        # break
