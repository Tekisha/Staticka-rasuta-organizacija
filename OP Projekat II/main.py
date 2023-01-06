from app.constants import *
from app.record import Record
from app.hash_file import HashFile
from datetime import datetime

active_file = None
def print_menu():
    print()
    print("--------------------------------------------------")
    print()
    print("1. Kreiraj novu datoteku")
    print("2. Izaberi aktivnu datoteku")
    print("3. Prikaz naziva aktivne datoteke")
    print("4. Prikaz svih slogova aktivne datoteke")
    print("5. Unesi novi polazak")
    print("6. Promeni datum i vreme polaska")
    print("7. Izbrisi polazak")
    print("Q za izlaz")
    print("--------------------------------------------------")
def create_new_file():
    while True:
        name = input("Unesi naziv nove datoteke: ")
        if name.strip()!="":
            break
        print("Naziv mora biti razlicit od praznog stringa.")

    rec = Record(ATTRIBUTES,FMT,CODING)
    fn = name+".dat"
    binary_file = HashFile(fn,rec,F,B)

    binary_file.init_file()
def choose_file():
    while True:
        name = input("Unesi naziv datoteke: ")
        if name.strip()!="":
            break
        print("Naziv mora biti razlicit od praznog stringa.")

    rec = Record(ATTRIBUTES,FMT,CODING)
    fn = name+".dat"
    binary_file = HashFile(fn,rec,F,B)

    try:
        with open(fn,'rb') as f:
            print()
    except:
        print("Ne postoji takva datoteka.")
        return None

    return binary_file



    
######################################################
def new_record():
    global active_file

    if active_file==None:
        print("Morate izabrati aktivnu datoteku.")
        return

    next=True

    id=None
    destination=""
    date1=0
    platform=""
    numOfSeats = 0

    while next:
        while True:
                id = input("Unesi evidencioni broj(7 cifara): ")
                if id.isdigit() and len(id)==7:
                    break
                print("Morate unijeti 7-cifreni broj.")
        
        rec_location = active_file.find_by_id(int(id))

        if rec_location != None:
            print("Uneti ID vec postoji.")
            return
        
        while True:
            destination = input("Unesi odrediste (<=50 karaktera): ") 
            if len(destination)>0 and len(destination)<=50:
                break
            print("Unos mora biti <=50karaktera")
        
        while True:
            date = input("Unesi datum i vreme(dd.mm.yyyy H:M): ")
            try:
                date1=datetime.strptime(date,"%d.%m.%Y %H:%M").timestamp()
                #print(date1)
                break
            except:
                print("Morate uneti ispravan format.")
        
        while True:
            platform = input("Unesi oznaku perona(3 karaktera): ")
            if len(platform)==3:
                break
            print("Morate uneti 3 karaktera.")
        
        while True:
            numOfSeats = input("Unesi broj mjesta (<=500 mjesta): ")
            try:
                numOfSeats = int(numOfSeats)
                if numOfSeats>0 and numOfSeats<=500:
                    break
                print("Morate uneti broj mesta <=500.")
            except:
                print("Morate uneti broj mesta.")
        

        new_rec = {
                    "id": int(id),
                    "destination": destination,
                    "date": int(date1),
                    "platform": platform,
                    "numOfSeats" : int(numOfSeats),
                    "status": 1,
                }
        
        active_file.insert_record(new_rec)

        while True:
            stop=input("Da li zelite da unesete novu vrednost? (y/n)")
            if stop.lower() == 'n':
                next=False
                break
            elif stop.lower() == 'y':
                break
            print("Morate uneti y ili n.")

    
def update_record():
    global active_file

    if active_file==None:
        print("Morate izabrati aktivnu datoteku.")
        return

    next=True

    id=None
    date1=0

    while next:
        while True:
            id = input("Unesi evidencioni broj(7 cifara): ")
            if id.isdigit() and len(id)==7:
                break
            print("Morate unijeti 7-cifreni broj.")
    
        rec_location = active_file.find_by_id(int(id))

        if rec_location == None:
            print("Polazak sa trazenim IDem ne postoji.")
            return
        
        while True:
                date = input("Unesi datum i vreme(dd.mm.yyyy H:M): ")
                try:
                    date1=datetime.strptime(date,"%d.%m.%Y %H:%M").timestamp()
                    #print(date1)
                    break
                except:
                    print("Morate uneti ispravan format.")
        

        block_idx = rec_location[0]
        rec_idx = rec_location[1]

        active_file.update_record(block_idx,rec_idx,date1)   

        while True:
            stop=input("Da li zelite da izmenite novu vrednost? (y/n)")
            if stop.lower() == 'n':
                next=False
                break
            elif stop.lower() == 'y':
                break
            print("Morate uneti y ili n.")


def delete_record():
    global active_file

    if active_file==None:
        print("Morate izabrati aktivnu datoteku.")
        return

    next=True

    id=None

    while next:
        while True:
            id = input("Unesi evidencioni broj(7 cifara): ")
            if id.isdigit() and len(id)==7:
                break
            print("Morate unijeti 7-cifreni broj.")
    
        rec_location = active_file.find_by_id(int(id))

        if rec_location == None:
            print("Polazak sa trazenim IDem ne postoji.")
            return
        
        block_idx = rec_location[0]
        rec_idx = rec_location[1]

        active_file.delete_record(block_idx,rec_idx)   

        while True:
            stop=input("Da li zelite da izbrisete novu vrednost? (y/n)")
            if stop.lower() == 'n':
                next=False
                break
            elif stop.lower() == 'y':
                break
            print("Morate uneti y ili n.")
        


def main():
    global active_file
    while True:
        print()
        print_menu()
        while True:
            ans = input("Izaberi opciju: ")
            if ans in ['1','2','3','4','5','6','7','1.','2.','3.','4.','5.','6.','7.','q','Q']:
                break
            print("Morate unijeti ponudjeni broj.")
        
        if ans in ['q','Q']:
            break

        if ans in ['1','1.']:
            create_new_file()
        elif ans in ['2','2.']:
            active_file = choose_file()
        elif ans in ['3','3.']:
            if active_file!=None:
                print(str(active_file.filename))
            else:
                print("Nijedna datoteka nije aktivna.")
        elif ans in ['4','4.']:
            if active_file!=None:
                active_file.print_file()
            else:
                print("Aktivna datoteka nije izabrana.")
        elif ans in ['5','5.']:
            new_record()
        elif ans in ['6','6.']:
            update_record()
        elif ans in ['7','7.']:
            delete_record()
        else:
            print("Morate unijeti neki od ponudjenih opcija.")
if __name__=="__main__":
    main()