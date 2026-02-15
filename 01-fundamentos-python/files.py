import os

dir_path = os.path.dirname(__file__)
file_path = os.path.join(dir_path, 'test.txt')

try:
    with open(file_path, mode='w') as my_file:
        text = my_file.write(":) ")
        
    with open(file_path, mode='r') as my_file:
        print(my_file.readlines())
        
    with open(file_path, mode='r+') as my_file:
        print(my_file.readlines())
        text = my_file.write("Hello world!")
        
    with open(file_path, mode='a') as my_file:
        text = my_file.write("123")
        print(text)
except FileNotFoundError:
    print("El archivo no existe")
except Exception as err:
    print (f"Ocurrio un error: {err}")