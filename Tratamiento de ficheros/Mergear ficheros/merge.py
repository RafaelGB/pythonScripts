# Python Program - Merge Two Files

import shutil;
print("Introduce 'x' para salir.");
filename1 = input("Introduce el primer nombre de fichero a mergear: ");
if filename1 == 'x':
    exit();
else:
    filename2 = input("Introduce el segundo nombre de fichero a mergear: ");
    filename3 = input("Crear nuevo fichero a juntar el merge de ambos ficheros: ");
    print();
    print("Mergeando en el fichero ",filename3);
    with open(filename3, "wb") as wfd:
        for f in [filename1, filename2]:
            with open(f, "rb") as fd:
                shutil.copyfileobj(fd, wfd, 1024*1024*10);
    print("\nContenido mergeado correctamente.!");
    print("(Quieres verlo? (y/n): ");
    check = input();
    if check == 'n':
        exit();
    else:
        print();
        c = open(filename3, "r");
        print(c.read());
        c.close();