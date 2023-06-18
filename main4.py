# from multiprocessing import Pool

# def readSerial(port) : 
#     print(port)

# numbers = [1, 2]
# with Pool(5) as p:
#         print(p.map(readSerial, [1, 2, 3]))

# from multiprocessing import Process

# def f(name):
#     print('hello', name)

# if __name__ == '__main__':
#     p = Process(target=f, args=('bob',))
#     p.start()
#     p.join()


# from multiprocessing import Process

# def f(name):
#     print('hello', name)
#     a = 0
#     while (a < 100):
#         print(a)
#         a += 1

# if __name__ == '__main__':
#     processes = []
#     names = ['bob', 'alice', 'charlie']  # List of names

#     for name in names:
#         p = Process(target=f, args=(name,))
#         processes.append(p)
#         p.start()

#     for p in processes:
#         p.join()