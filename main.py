import tkinter as tk
from tkinter import filedialog
import subprocess
import os


def get_filename_without_extension(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]


def get_file_size(file_path):
    return os.path.getsize(file_path) / (1024 * 1024)  # 轉換成 MB


def compress_video(input_file, crf, output_prefix):
    input_dir = os.path.dirname(input_file)
    file_name = get_filename_without_extension(input_file)

    if not output_prefix:
        compressed_file_name = os.path.join(input_dir, f"{file_name}_crf{crf}")
    else:
        compressed_file_name = os.path.join(
            input_dir, f"[{output_prefix}][{file_name}]_crf{crf}.mp4")
    cmd = f'ffmpeg -i "{input_file}" -crf {crf} "{compressed_file_name}.mp4" -y'
    print(cmd)
    subprocess.run(cmd, shell=True)

    return f"{compressed_file_name}.mp4"


def shutdown_after_compress():
    result_label.config(text="壓縮完成！正在準備關機...")
    subprocess.run("shutdown /s /t 1", shell=True)


def select_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("影片檔案", "*.mp4")])
    entry_file_path.delete(0, tk.END)
    entry_file_path.insert(0, file_paths)


def process_files():
    input_files = entry_file_path.get().split()
    crf_value = int(entry_crf.get()) if entry_crf.get() else 27
    output_prefix = entry_output_prefix.get()
    max_file_size = float(entry_max_file_size.get(
    )) if entry_max_file_size.get() else 200.0
    mini_file_size = float(entry_mini_file_size.get(
    )) if entry_mini_file_size.get() else 170.0
    ignore_file_size = checkbox_ignore_file_size_var.get()
    shutdown_after_compress_var = checkbox_shutdown_var.get()
    print("ignore_file_size", ignore_file_size)

    try:
        crf_value = int(crf_value)
    except ValueError:
        result_label.config(text="CRF必須是有效的整數。")
        return

    if not input_files or not crf_value:
        result_label.config(text="請填寫所有欄位。")
        return

    for input_file in input_files:
        curr_crf_value = crf_value
        try:
            final_file_name = ""
            print(input_file)
            unzip_file_size = get_file_size(input_file)
            print("unzip_file_size", unzip_file_size)
            print("mini_file_size", mini_file_size)

            if not ignore_file_size and not unzip_file_size <= mini_file_size:
                compressed_file_name = compress_video(
                    input_file, curr_crf_value, output_prefix)
                compressed_file_size = get_file_size(compressed_file_name)
                initial_file_size = compressed_file_size
                final_file_name = compressed_file_name

                while initial_file_size > max_file_size or initial_file_size < mini_file_size:
                    if initial_file_size > max_file_size:
                        if initial_file_size >= max_file_size + 50:
                            curr_crf_value += 2
                        else:
                            curr_crf_value += 1
                    elif initial_file_size < mini_file_size:
                        if initial_file_size <= mini_file_size - 50:
                            curr_crf_value -= 2
                        else:
                            curr_crf_value -= 1

                    compressed_file_path = compress_video(
                        input_file, curr_crf_value, output_prefix)
                    final_file_name = compressed_file_path
                    compressed_file_size = get_file_size(
                        compressed_file_path)
                    print(
                        f"重新壓縮 (CRF={curr_crf_value}), 壓縮後檔案大小: {compressed_file_size:.2f} MB")
                    initial_file_size = compressed_file_size

                    if mini_file_size <= initial_file_size <= max_file_size:
                        break

                if output_prefix:
                    file_name = get_filename_without_extension(input_file)
                    file_dir = os.path.dirname(final_file_name)
                    os.rename(final_file_name,
                              f"{file_dir}/[{output_prefix}][{file_name}].mp4")
            else:
                compress_video(input_file, curr_crf_value, output_prefix)

            if shutdown_after_compress_var:
                shutdown_after_compress()

        except Exception as e:
            result_label.config(text=f"處理 {input_file} 時發生錯誤: {str(e)}")

    result_label.config(text="壓縮完成！")


# 建立主視窗
window = tk.Tk()
window.title("影片壓縮工具")

# 建立並放置小工具
label_file_path = tk.Label(window, text="選擇 MP4 檔案:")
label_file_path.grid(row=0, column=0, padx=10, pady=10)

entry_file_path = tk.Entry(window, width=40)
entry_file_path.grid(row=0, column=1, padx=10, pady=10)

button_browse = tk.Button(window, text="瀏覽", command=select_files)
button_browse.grid(row=0, column=2, padx=10, pady=10)

label_crf = tk.Label(window, text="輸入 CRF 值:")
label_crf.grid(row=1, column=0, padx=10, pady=10)

entry_crf = tk.Entry(window, width=10)
entry_crf.insert(0, "27")
entry_crf.grid(row=1, column=1, padx=10, pady=10)

label_output_prefix = tk.Label(window, text="輸入輸出前綴:")
label_output_prefix.grid(row=2, column=0, padx=10, pady=10)

entry_output_prefix = tk.Entry(window, width=20)
entry_output_prefix.grid(row=2, column=1, padx=10, pady=10)

label_max_file_size = tk.Label(window, text="最大檔案大小 (MB):")
label_max_file_size.grid(row=3, column=0, padx=10, pady=10)

entry_max_file_size = tk.Entry(window, width=10)
entry_max_file_size.insert(0, "200")
entry_max_file_size.grid(row=3, column=1, padx=10, pady=10)

label_mini_file_size = tk.Label(window, text="最小檔案大小 (MB):")
label_mini_file_size.grid(row=4, column=0, padx=10, pady=10)

entry_mini_file_size = tk.Entry(window, width=10)
entry_mini_file_size.insert(0, "170")
entry_mini_file_size.grid(row=4, column=1, padx=10, pady=10)

checkbox_ignore_file_size_var = tk.BooleanVar()
checkbox_ignore_file_size = tk.Checkbutton(
    window, text="忽略檔案大小", variable=checkbox_ignore_file_size_var)
checkbox_ignore_file_size.grid(row=5, column=0, columnspan=3, pady=10)

checkbox_shutdown_var = tk.BooleanVar()
checkbox_shutdown = tk.Checkbutton(
    window, text="壓縮完後自動關機", variable=checkbox_shutdown_var)
checkbox_shutdown.grid(row=6, column=0, columnspan=3, pady=10)

button_compress = tk.Button(window, text="壓縮影片", command=process_files)
button_compress.grid(row=7, column=0, columnspan=3, pady=10)

result_label = tk.Label(window, text="")
result_label.grid(row=8, column=0, columnspan=3, pady=10)

# 啟動 GUI 事件迴圈
window.mainloop()
