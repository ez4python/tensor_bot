import tkinter as tk
from tkinter import scrolledtext, messagebox
import json
import os


class NERTaggerApp:
    def __init__(self, master):
        self.master = master
        master.title("NER Annotatsiya Dasturi")
        master.geometry("1000x800")

        self.tags = [
                "FROM","TO", "CARGO", "WEIGHT", "FREIGHT",
                "ADVANCE", "DESTINATION_TYPE", "VEHICLE", "VEHICLE_QUANTITY",
                "LOADING_TIME", "UNLOADING_DESTINATION", "CARGO_CONDITION",
                "PHONENUMBER","LOADING_LOCATION", "PERMIT", "ADDITIONAL","USER"  # Umumiy qo'shimcha teglar
        ]
        self.entities = []
        self.current_text = ""  # Matn o'zgarganini kuzatish uchun

        self.create_widgets()

    def create_widgets(self):
        # Matn kiritish qismi
        self.text_label = tk.Label(self.master, text="E'lon matnini kiriting:", font=("Arial", 12))
        self.text_label.pack(pady=5)

        self.text_input = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, width=100, height=10, font=("Arial", 12),
                                                    state='normal')  # Holatini 'normal' deb belgilaymiz
        self.text_input.pack(pady=5)
        # Matn o'zgarganda yoki tanlash bekor bo'lganda tetiklash uchun
        self.text_input.bind("<<Selection>>", self.on_selection_change)  # Tanlash o'zgarganda
        self.text_input.bind("<KeyRelease>", self.on_text_change)  # Matn o'zgarganda

        # Teg tugmalari qismi
        self.tag_frame = tk.Frame(self.master)
        self.tag_frame.pack(pady=10)

        row_num = 0
        col_num = 0
        for tag in self.tags:
            button = tk.Button(self.tag_frame, text=tag, command=lambda t=tag: self.add_entity(t),
                               font=("Arial", 10), width=15, height=2)
            button.grid(row=row_num, column=col_num, padx=5, pady=5)
            col_num += 1
            if col_num > 4:  # Har qatorda 5 ta tugma
                col_num = 0
                row_num += 1

        # Boshqaruv tugmalari
        self.control_frame = tk.Frame(self.master)
        self.control_frame.pack(pady=10)

        self.clear_selection_btn = tk.Button(self.control_frame, text="Tanlashni Tozalash",
                                             command=self.clear_selection, font=("Arial", 10))
        self.clear_selection_btn.grid(row=0, column=0, padx=5)

        self.reset_btn = tk.Button(self.control_frame, text="Hammasini Tozalash", command=self.reset_all,
                                   font=("Arial", 10))
        self.reset_btn.grid(row=0, column=1, padx=5)

        self.save_to_json_btn = tk.Button(self.control_frame, text="JSON faylga saqlash",
                                          command=self.save_to_json_file, font=("Arial", 10))
        self.save_to_json_btn.grid(row=0, column=2, padx=5)

        # Natija oynasi
        self.result_label = tk.Label(self.master, text="Natija (JSON):", font=("Arial", 12))
        self.result_label.pack(pady=5)

        self.result_output = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, width=100, height=15,
                                                       font=("Arial", 12), state='disabled')
        self.result_output.pack(pady=5)

    def on_selection_change(self, event=None):
        # Foydalanuvchi matnni tanlaganda yoki tanlash bekor bo'lganda ishlaydi
        if self.current_text != self.text_input.get("1.0", tk.END).strip():
            # Agar matn o'zgargan bo'lsa, barchasini tozalash kerak
            self.reset_all()  # Bu qator takroriy chaqiruvga olib kelmasligi kerak
        self.current_text = self.text_input.get("1.0", tk.END).strip()
        self.display_current_json()  # Har safar tanlash o'zgarganda JSONni yangilash

    def on_text_change(self, event=None):
        # Foydalanuvchi matnni kiritganda yoki o'zgartirganda ishlaydi
        new_text = self.text_input.get("1.0", tk.END).strip()
        if self.current_text != new_text:
            # Agar matn o'zgargan bo'lsa, avvalgi belgilashlarni tozalaymiz
            self.reset_all()  # Faqat matn haqiqatda o'zgarganda tozalaymiz
            self.current_text = new_text
        self.display_current_json()

    def add_entity(self, tag_name):
        try:
            # Tanlangan matnning Tkinter indekslarini olish
            start_index_tk = self.text_input.index(tk.SEL_FIRST)
            end_index_tk = self.text_input.index(tk.SEL_LAST)

            selected_text = self.text_input.get(start_index_tk, end_index_tk)

            # Tkinter indekslarini Python string indekslariga o'tkazish
            full_text = self.text_input.get("1.0", tk.END + "-1c")  # Oxirgi '\n' ni olib tashlash

            # Tkinter get("1.0", index_str) matnning boshidan index_str gacha bo'lgan qismini qaytaradi.
            # Uning uzunligi Python stringidagi o'sha pozitsiyani bildiradi.
            start_char_idx = len(self.text_input.get("1.0", start_index_tk))
            end_char_idx = len(self.text_input.get("1.0", end_index_tk))

            # Agar tanlangan matn bo'sh bo'lsa
            if not selected_text:
                messagebox.showwarning("Ogohlantirish", "Iltimos, avval matnni belgilang.")
                return

            # Agar Python stringidagi indekslar bo'yicha matn mos kelmasa, xato
            # (Bu kamdan-kam holat, lekin Tkinter versiyasiga bog'liq bo'lishi mumkin)
            if full_text[start_char_idx:end_char_idx] != selected_text:
                messagebox.showerror("Xato",
                                     "Indekslash xatosi: Tanlangan matn Python indeksi bo'yicha to'g'ri kelmadi. Iltimos, muallifga xabar bering.")
                return

            # Oldingi qo'shilgan teglar bilan kesishishni tekshirish
            for existing_start, existing_end, existing_tag in self.entities:
                if not (end_char_idx <= existing_start or start_char_idx >= existing_end):
                    messagebox.showwarning("Ogohlantirish",
                                           f"Belgilangan '{selected_text}' '{tag_name}' tegi, '{full_text[existing_start:existing_end]}' '{existing_tag}' tegi bilan kesishmoqda. Bitta matn qismi faqat bitta tegga ega bo'lishi kerak.")
                    return  # Qo'shmaslik

            self.entities.append([start_char_idx, end_char_idx, tag_name])
            self.entities.sort(key=lambda x: x[0])  # Start indeks bo'yicha saralash
            self.display_current_json()
            self.highlight_text()

        except tk.TclError:  # Matn tanlanmaganda SEL_FIRST/SEL_LAST bo'lmaydi
            messagebox.showwarning("Ogohlantirish", "Iltimos, avval matnni belgilang.")
        except Exception as e:
            messagebox.showerror("Xato", f"Kutilmagan xato yuz berdi: {e}")
            print(f"DEBUG info: {e}")  # Debugging uchun konsolga chiqarish

    def clear_selection(self):
        try:
            # Tanlangan matnni tozalash
            self.text_input.tag_remove(tk.SEL, "1.0", tk.END)
        except tk.TclError:
            pass  # Tanlash mavjud emasligi

    def reset_all(self):
        # Matn maydonini tozalash
        self.text_input.delete("1.0", tk.END)
        self.entities = []
        self.current_text = ""  # Joriy matnni ham tozalash

        # Natija oynasini tozalash
        self.result_output.config(state='normal')
        self.result_output.delete("1.0", tk.END)
        self.result_output.config(state='disabled')

        # Belgilashlarni olib tashlash
        self.remove_highlights()

    def display_current_json(self):
        # JSONni shakllantirish
        current_data = {
            "text": self.text_input.get("1.0", tk.END).strip(),
            "entities": self.entities
        }
        # Natija oynasini yangilash
        self.result_output.config(state='normal')
        self.result_output.delete("1.0", tk.END)
        self.result_output.insert(tk.END, json.dumps(current_data, indent=2, ensure_ascii=False))
        self.result_output.config(state='disabled')

    def highlight_text(self):
        self.remove_highlights()  # Oldingi belgilashlarni olib tashlash
        self.text_input.tag_configure("highlight", background="yellow")  # Belgilash rangini sariq qilish

        for start, end, tag in self.entities:
            # Python indekslarini Tkinter indekslariga o'tkazish
            start_idx_tk = self.text_input.index(f"1.0 + {start}c")
            end_idx_tk = self.text_input.index(f"1.0 + {end}c")
            self.text_input.tag_add("highlight", start_idx_tk, end_idx_tk)

    def remove_highlights(self):
        self.text_input.tag_remove("highlight", "1.0", tk.END)

    def save_to_json_file(self):
        file_path = "cleaned_data.json"  # JSON faylining nomi

        current_entry = {
            "text": self.text_input.get("1.0", tk.END).strip(),
            "entities": self.entities
        }

        # Agar matn va teglar bo'sh bo'lsa, saqlamaymiz
        if not current_entry["text"] or not current_entry["entities"]:
            messagebox.showwarning("Ogohlantirish", "Saqlash uchun matn va belgilangan teglar mavjud emas.")
            return

        existing_data = []
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = []  # Agar fayl ro'yxat bo'lmasa, uni bo'sh deb hisoblash
            except json.JSONDecodeError:
                messagebox.showwarning("Ogohlantirish",
                                       f"{file_path} fayli JSON formatida emas yoki buzilgan. Yangi fayl yaratiladi.")
                existing_data = []

        # Dublikatlarni oldini olish (agar matn va entitylar to'liq bir xil bo'lsa)
        # Bu juda muhim, chunki takroriy misollar modelni noto'g'ri o'qitishga olib kelishi mumkin
        is_duplicate = False
        for entry in existing_data:
            if entry.get("text") == current_entry["text"] and entry.get("entities") == current_entry["entities"]:
                is_duplicate = True
                break

        if not is_duplicate:
            existing_data.append(current_entry)
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("Muvaffaqiyat", f"Ma'lumot '{file_path}' fayliga muvaffaqiyatli saqlandi.")
                self.reset_all()  # Saqlagandan so'ng hamma narsani tozalash
            except Exception as e:
                messagebox.showerror("Xato", f"Faylni saqlashda xato yuz berdi: {e}")
        else:
            messagebox.showwarning("Ogohlantirish", "Bu yozuv allaqachon datasetda mavjud. Saqlanmadi.")


if __name__ == "__main__":
    root = tk.Tk()
    app = NERTaggerApp(root)
    root.mainloop()