import heapq
import csv
import os

class PriorityQueue:
    def __init__(self):
        self.heap = []
        self.index = 0

    def push(self, item, priority):
        if item["Kelompok Rentan"].lower() == "bukan kelompok rentan":
            priority += self.index / 100000
        heapq.heappush(self.heap, (priority, -item["Umur"], self.index, item))
        self.index += 1

    def pop(self):
        return heapq.heappop(self.heap)[-1]

    def remove_by_name(self, name):
        name = name.lower()
        for i, (_, _, _, item) in enumerate(self.heap):
            if item["Nama"].lower() == name:
                del self.heap[i]
                heapq.heapify(self.heap)
                return True
        return False

    def search_by_name(self, name):
        name = name.lower()
        sorted_queue = self.to_list()
        for idx, (_, _, _, item) in enumerate(sorted_queue):
            if item["Nama"].lower() == name:
                return idx + 1, item
        return None, None

    def to_list(self):
        return sorted(self.heap, key=lambda x: (x[0], -x[1], x[2]))

def save_to_csv(priority_queue, filename='antrianbansos.csv'):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Priority", "Umur", "Index", "Nama", "Kelompok Rentan"])
        for priority, neg_age, index, item in priority_queue.to_list():
            writer.writerow([priority, -neg_age, index, item['Nama'], item['Kelompok Rentan']])

def load_from_csv(priority_queue, filename='antrianbansos.csv'):
    if not os.path.exists(filename):
        return
    try:
        with open(filename, mode='r') as file:
            reader = csv.reader(file)
            header = next(reader)
            if header:
                for row in reader:
                    priority = float(row[0]) if row[0] else 0.0
                    umur = int(row[1])
                    index = int(row[2])
                    nama = row[3]
                    kelompok_rentan = row[4]
                    data = {
                        "Nama": nama,
                        "Umur": umur,
                        "Kelompok Rentan": kelompok_rentan
                    }
                    priority_queue.index = max(priority_queue.index, index + 1)
                    heapq.heappush(priority_queue.heap, (priority, -umur, index, data))
    except (FileNotFoundError, StopIteration):
        pass

def display_menu():
    print("\nPeduli Antri Menu: ")
    print("1. Daftar Antrian")
    print("2. Hapus Antrian Berdasarkan Nama")
    print("3. Tampilkan Antrian")
    print("4. Cek Nomor Antrian Berdasarkan Nama")
    print("5. Konfirmasi Sudah Selesai Antri")
    print("6. Keluar")

def determine_priority(kelompok_rentan):
    priority_map = {
        'hamil': 1,
        'tua 1': 2,
        'tua 2': 3,
        'tua 3': 4,
        'disabilitas': 5,
        'menyusui': 6,
        'memiliki balita': 7,
        'bukan kelompok rentan': 8
    }
    return priority_map.get(kelompok_rentan.lower(), 8)

def determine_vulnerable_group(umur):
    if umur >= 70:
        return 'Tua 1'
    elif umur >= 60:
        return 'Tua 2'
    elif umur >= 50:
        return 'Tua 3'
    else:
        return 'Bukan Kelompok Rentan'

def clear_terminal():
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        _ = os.system('cls')

priority_queue = PriorityQueue()

load_from_csv(priority_queue)

while True:
    display_menu()
    choice = input("Pilih menu: ")

    if choice == '1':
        nama = input("Nama: ")
        umur = int(input("Umur: "))

        is_vulnerable = input("Apakah termasuk kelompok rentan? (Ketik : Ya/Tidak): ").lower()
        while is_vulnerable not in ['ya', 'tidak']:
            is_vulnerable = input("Mohon masukkan jawaban yang valid (Ketik : Ya/Tidak): ").lower()

        kelompok_rentan = 'Bukan Kelompok Rentan'
        if is_vulnerable == 'ya':
            print("Pilih menu untuk kelompok rentan:")
            print("1. Hamil")
            print("2. Menyusui")
            print("3. Disabilitas")
            print("4. Memiliki Balita")
            print("5. Tua")
            menu = input("Pilih menu: ")

            if menu == '1':
                kelompok_rentan = 'Hamil'
            elif menu == '2':
                kelompok_rentan = 'Menyusui'
            elif menu == '3':
                kelompok_rentan = 'Disabilitas'
            elif menu == '4':
                kelompok_rentan = 'Memiliki Balita'
            elif menu == '5':
                if umur < 50:
                    print("Umur anda masih muda untuk kelompok tua, Mohon masukkan data umur yang benar!")
                    continue
                else:
                    kelompok_rentan = determine_vulnerable_group(umur)

        elif umur >= 50:
            kelompok_rentan = determine_vulnerable_group(umur)

        priority = determine_priority(kelompok_rentan)

        data = {
            "Nama": nama,
            "Umur": umur,
            "Kelompok Rentan": kelompok_rentan
        }
        priority_queue.push(data, priority)
        save_to_csv(priority_queue)
        print("Data telah ditambahkan ke dalam antrian bantuan sosial. Nomor antrian Anda akan muncul dalam daftar antrian")

    elif choice == '2':
        if not priority_queue.heap:
            print("Queue kosong.")
        else:
            nama = input("Masukkan nama yang ingin dihapus: ")
            if priority_queue.remove_by_name(nama):
                save_to_csv(priority_queue)
                print(f"Data dengan nama {nama} telah dihapus dari queue.")
            else:
                print(f"Tidak ditemukan data dengan nama {nama}.")

    elif choice == '3':
        if not priority_queue.heap:
            print("Queue kosong.")
        else:
            print("Antrian berdasarkan prioritas:")
            sorted_queue = priority_queue.to_list()
            for i, (_, neg_age, _, item) in enumerate(sorted_queue, start=1):
                print(f"Nomor Antrian: {i}, Nama: {item['Nama']}, Umur: {item['Umur']}, Kelompok Rentan: {item['Kelompok Rentan']}")

    elif choice == '4':
        name = input("Masukkan nama yang ingin dicari: ")
        position, result = priority_queue.search_by_name(name)
        if result:
            print(f"Data ditemukan: Nomor Antrian: {position}, Nama: {result['Nama']}, Umur: {result['Umur']}, Kelompok Rentan: {result['Kelompok Rentan']}")
        else:
            print("Nama tidak ditemukan dalam antrian.")

    elif choice == '5':
        if not priority_queue.heap:
            print("Queue kosong.")
        else:
            item = priority_queue.pop()
            save_to_csv(priority_queue)
            print(f"Data dengan nama {item['Nama']} sudah selesai antri.")

    elif choice == '6':
        print("Program berakhir. Membersihkan terminal...")
        break

    else:
        print("Pilihan tidak valid. Silakan pilih menu yang benar.")

input("Tekan Enter untuk menutup program...")
clear_terminal()
