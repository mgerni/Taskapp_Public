

import tasklist

easy_dic = {}
for task, image in zip(tasklist.easy, tasklist.easy_images):
    easy_dic[task] = image

for x in easy_dic.items():
    print(x, y)
print(len(easy_dic))