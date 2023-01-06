#!/usr/bin/python

import os

from app.binary_file import BinaryFile


class HashFile(BinaryFile):
    def __init__(self, filename, record, blocking_factor, b, empty_key=-1,step=1):
        BinaryFile.__init__(self, filename, record, blocking_factor, empty_key)
        self.b = b
        self.step = step

    def hash(self, id):
        return id % self.b

    def init_file(self):
        with open(self.filename, "wb") as f:
            for _ in range(self.b):
                block = self.blocking_factor*[self.get_empty_rec()]
                self.write_block(f, block)


    def update_record(self,block_idx,rec_idx,date):

        with open(self.filename, 'rb+') as f:
           f.seek(block_idx * self.block_size)
           block =self.read_block(f)

           block[rec_idx]["date"]=date

           f.seek(block_idx * self.block_size)
           self.write_block(f, block)
    
    def delete_record(self,block_idx,rec_idx):
        with open(self.filename,'rb+') as f:
            f.seek(block_idx * self.block_size)
            block =self.read_block(f)

            #brise slog
            block[rec_idx] =self.get_empty_rec()

            i=rec_idx+1
            while i>=1 and i<self.blocking_factor and block[i]["status"]!=0:
                block[i-1]=block[i]
                block[i] = self.get_empty_rec()
                i+=1
            
            f.seek(block_idx * self.block_size)
            self.write_block(f,block)

            #ako je maticni baket bio pun traze se prekoracioci
            if i==self.blocking_factor:
                self.__check_overflow(f,block_idx,self.hash(block_idx+self.step))
    

    #provjerava da li se nalazi neki prekoracilac koji odgovara maticnom baketu
    def __check_overflow(self,f,primary_block_idx,current_block_idx):

        if current_block_idx!=primary_block_idx:
            f.seek(current_block_idx*self.block_size)
            block = self.read_block(f)

            i=0

            while i<self.blocking_factor and block[i].get("status"):
                #ako je pronasao prekoracilac koji pripada maticnom baketu
                #smjesta ga u maticni
                if self.hash(block[i]["id"]) == primary_block_idx:
                    f.seek(primary_block_idx*self.block_size)
                    primary_block = self.read_block(f)
                    primary_block[self.blocking_factor-1] = block[i]

                    f.seek(primary_block_idx*self.block_size)
                    self.write_block(f,primary_block)

                    block[i] = self.get_empty_rec()

                    #rotira u trenutnom baketu sve slogove u lijevo

                    j=i+1
                    while j>=1 and j<self.blocking_factor and block[j]["status"]!=0:
                        block[j-1]=block[j]
                        block[j] = self.get_empty_rec()
                        j+=1
                    
                    f.seek(current_block_idx * self.block_size)
                    self.write_block(f,block)

                    #ako je baket bio pun traze se prekoracioci
                    if j==self.blocking_factor:
                        self.__rotate_left(f,current_block_idx,current_block_idx,self.hash(current_block_idx+self.step)) #srediti funkciju
                    #ako je naislo na slobodnu lokaciju kraj trazenja
                    return
                i+=1
            
            #ako nije pronasao nijedan odgovarajuci prekoracilac
            #ide na sledeci
            if i==self.blocking_factor:
                self.__check_overflow(f,primary_block_idx,self.hash(current_block_idx+self.step))
                return
            #ako je dosao do prazne lokacije bez pronalaska odgovarajuceg prekoracioca
            #rotira sve prekoracioce koje moze
            self.__rotate_left(f,primary_block_idx,primary_block_idx,self.hash(primary_block_idx+self.step))
            return

        elif primary_block_idx==current_block_idx:
            self.__rotate_left(f,current_block_idx,current_block_idx,self.hash(current_block_idx+self.step))
            return
    
    #rotira sve prekoracioce u lijevo pri brisanju
    def __rotate_left(self,f,primary_block_idx,last_block_idx,current_block_idx):

        if current_block_idx!=primary_block_idx:
            f.seek(current_block_idx*self.block_size)
            block = self.read_block(f)

            i=0

            while i<self.blocking_factor and block[i].get("status"):
                #ako je pronasao slog koji je prekoracilac
                if self.hash(block[i]["id"])!=current_block_idx:
                    
                    #da prekoracilac ne bi otisao iza svog maticnog baketa
                    parent_block_idx = self.hash(block[i]["id"])

                    #racunamo koliko baketa je trenutno udaljen od maticnog
                    current_distance = current_block_idx-parent_block_idx
                    if current_distance<0:
                        current_distance=self.b-abs(current_distance)

                    #racunamo koliko baketa bi bio udaljen ako bi se rotirao
                    possible_distance = last_block_idx - parent_block_idx
                    if possible_distance<0:
                        possible_distance=self.b-abs(possible_distance)
                    
                    #ako bi udaljenost bila veca kad bi se rotirao, preskacemo slog
                    if possible_distance>current_distance:
                        i+=1
                        continue

                    

                    #inace ga rotiramo
                    f.seek(last_block_idx*self.block_size)
                    last_block = self.read_block(f)
                    last_block[self.blocking_factor-1] = block[i]

                    f.seek(last_block_idx*self.block_size)
                    self.write_block(f,last_block)

                    block[i] = self.get_empty_rec()

                    #rotira u baketu sve u lijevo
                    j=i+1
                    while j>=1 and j<self.blocking_factor and block[j]["status"]!=0:
                        block[j-1]=block[j]
                        block[j] = self.get_empty_rec()
                        j+=1
                    
                    f.seek(current_block_idx * self.block_size)
                    self.write_block(f,block)

                    #ako je baket bio pun traze se prekoracioci
                    if j==self.blocking_factor:
                        self.__rotate_left(f,primary_block_idx,current_block_idx,self.hash(current_block_idx+self.step))
                    #ako nije bio pun,kraj
                    return
                i+=1
            
            #ako je baket pun i nista nismo rotirali ide na sledeci
            if i==self.blocking_factor:
                self.__rotate_left(f,primary_block_idx,last_block_idx,self.hash(current_block_idx+self.step))
            #kraj ako je naislo na slobodnu lokaciju u baketu
            return

        elif primary_block_idx==current_block_idx:
            #kraj ako je stiglo do baketa od kog je pocelo pomjeranje
            return


    def __insert_overflow(self,f,rec,block_idx,next_block_idx,id):
        
        #dok ne dodje do kraja datoteke i dok ne naidje na maticni
        if next_block_idx < self.b and next_block_idx!=block_idx:
            f.seek(next_block_idx*self.block_size)
            block = self.read_block(f)

            i=0
            #while petlja dok ne dodje do kraja baketa ili slobodne lokacije
            while i<self.blocking_factor and block[i].get("status"):
                #ako je pronasao slog sa istim slogom provjera statusa
                if block[i].get("id") == id:
                    if block[i].get("status") == 1:
                        print("Already exists with ID {}".format(id))
                    else:
                        block[i] = rec
                        f.seek(next_block_idx*self.block_size)
                        self.write_block(f,block)
                    return
                i+=1
            
            #ako je doslo do kraja baketa ide na sledeci baket
            if i == self.blocking_factor:
                self.__insert_overflow(f,rec,block_idx,next_block_idx+self.step,id)
                return
            
            #ako je pronaslo slobodnu lokaciju upise slog
            block[i] = rec
            f.seek(next_block_idx*self.block_size)
            self.write_block(f,block)

        elif block_idx==next_block_idx:
            #ako je stiglo do maticnog baketa
            print("Upis neuspesan. Cela datoteka je popunjena.")
        else:
            #ako je stiglo do kraja datoteke vraca se na prvi baket
            self.__insert_overflow(f,rec,block_idx,0,id)
    
    def insert_record(self, rec):
        id = rec.get("id")
        block_idx = self.hash(id)

        with open(self.filename, "rb+") as f:
            f.seek(block_idx * self.block_size)
            block = self.read_block(f)

            i = 0
            while i < self.blocking_factor and block[i].get("status"):
                if block[i].get("id") == id:
                    if block[i].get("status") == 1:
                        print("Already exists with ID {}".format(id))
                    else:
                        block[i] = rec
                        f.seek(block_idx * self.block_size)
                        self.write_block(f, block)
                    return
                i += 1

            if i == self.blocking_factor:
                self.__insert_overflow(f, rec,block_idx,block_idx+self.step,id)
                return

            block[i] = rec
            f.seek(block_idx * self.block_size)
            self.write_block(f, block)
    
    def print_file(self):
        with open(self.filename, "rb") as f:
            for i in range(self.b):
                block = self.read_block(f)
                print("Bucket {}".format(i+1))
                self.print_block(block)

    def __find_in_overflow(self,f,id,block_idx,next_block_idx):
        #dok ne dodje do kraja datoteke i dok ne naidje na maticni
        if next_block_idx < self.b and next_block_idx!=block_idx:
            f.seek(next_block_idx*self.block_size)
            block = self.read_block(f)

            i=0
            #while petlja dok ne dodje do kraja baketa ili slobodne lokacije
            while i<self.blocking_factor and block[i].get("status"):
                #ako je pronasao slog sa istim slogom provjera statusa
                if block[i].get("id") == id:
                    if block[i].get("status") == 1:
                        return (next_block_idx,i)
                    else:
                        #print("Trazenje neuspesno.")
                        return None
                i+=1
            
            #ako je doslo do kraja baketa ide na sledeci baket
            if i == self.blocking_factor:
                return self.__find_in_overflow(f,id,block_idx,next_block_idx+self.step)
                
            #ako je pronaslo slobodnu lokaciju u baketu znaci da ne postoji trazeni id
            #print("Trazenje neuspesno.")
            return None
        
        elif block_idx==next_block_idx:
            #ako je stiglo do maticnog baketa
            print("Trazenje neuspesno.")
            return None
        else:
            #ako je stiglo do kraja datoteke vraca se na prvi baket
            return self.__find_in_overflow(f,id,block_idx,0)



    # def __find_in_overflow(self, f, id):
    #     f.seek(self.b * self.block_size)

    #     i = 0
    #     while True:
    #         rec = self.read_record(f)
    #         if not rec:
    #             return None
    #         if rec.get("id") == id:
    #             return (self.b, i)
    #         i += 1

    def find_by_id(self, id):
        block_idx = self.hash(id)

        with open(self.filename, "rb+") as f:
            f.seek(block_idx * self.block_size)
            block = self.read_block(f)

            for i in range(self.blocking_factor):
                if block[i].get("status") == 0:
                    return None
                if block[i].get("status") == 1 and block[i].get("id") == id:
                    return (block_idx, i)

            return self.__find_in_overflow(f, id,block_idx,block_idx+self.step)

        return None

    def delete_by_id_logic(self, id):
        found = self.find_by_id(id)

        if not found:
            return None

        block_idx = found[0]
        rec_idx = found[1]

        with open(self.filename, "rb+") as f:
            f.seek(block_idx * self.block_size)
            block = self.read_block(f)
            block[rec_idx]["status"] = 2
            f.seek(block_idx * self.block_size)
            self.write_block(f, block)
            return found
    

