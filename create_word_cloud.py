import os.path
from datetime import datetime

import jieba, codecs, sys, pandas
import imageio
from wordcloud import WordCloud, ImageColorGenerator
from os import listdir,makedirs
from os.path import isfile, join

stopwords_filename = 'data/stopwords.txt'
font_filename = 'fonts/STFangSong.ttf'
template_dir = 'data/templates/'
#创建一个列表，它包含各个template的文件名
pic_list=['color_love.png','love.png']
#生成的文件所存放的路径
output_dir='output'
stopwords=None
# 我们的项目：模板图片的路径应该是写定的。用户或许有机会选择模板
#保存路径是写定的。生成的时候是根据字符串生成而不是找文件
def generate_by_text(text):
    global stopwords
    # 读取stopwords_filename对应的停用词文件 逐行获得停用词
    if stopwords==None:
        print('重置停用词')
        stopwords = set([line.strip()
                     for line in codecs.open(stopwords_filename, 'r', 'utf-8')])
    # 如果没有output_dir这个文件夹，就创建一个
    if not os.path.isdir(output_dir):
        makedirs(output_dir)
    segs = jieba.cut(text)  # 用jieba对内容进行分词
    words = []
    for seg in segs:
        word = seg.strip().lower()
        if len(word) > 1 and word not in stopwords:
            words.append(word)  # 去掉前后空格，转换为小写，去掉停用词，然后加入到words列表中

    words_df = pandas.DataFrame({'word': words})  # 将words列表转换为pandas的DataFrame格式
    words_stat = words_df.groupby(by=['word']).size().reset_index(name='number')  # 按照word列进行分组，然后统计每组的数量
    words_stat = words_stat.sort_values(by="number", ascending=False)  # 排序

    print('不同词语的数量 =', len(words_stat))
#根据现在的时间获得一个字符串
    input_prefix=datetime.now().strftime('%H_%M_%S')

    for file in pic_list:
        background_picture_filename = join(template_dir, file)  # 获得所有以.jpg或.png结尾的文件，存进background_picture_filename
        if isfile(background_picture_filename):  # 确认是否是文件
            prefix = file.split('.')[0]  # 图片名字的前缀
            bimg = imageio.v2.imread(background_picture_filename)
            # 直接用WordCloud函数 传入字体路径、背景颜色、遮罩图片、最大字体大小、随机状态
            wordcloud = WordCloud(font_path=font_filename, background_color='white', mask=bimg, max_font_size=600,
                                  random_state=100)
            # 用fit_words函数传入words_stat的前4000个元素，iterrows()返回一个迭代器，每次迭代返回一个元组，元组的第一个元素是行索引，第二个元素是Series
            # index=false表示不返回行索引
            wordcloud = wordcloud.fit_words(dict(words_stat.head(4000).itertuples(index=False)))
            bimgColors = ImageColorGenerator(bimg)  # 把图片的颜色存入bimgColors
            wordcloud.recolor(color_func=bimgColors)  # 对词云进行着色
            # 输出路径为图片名字的前缀+输入文件名字的前缀+.png
            output_filename =output_dir+'/'+ prefix + '_' + input_prefix + '.png'
            print('保存路径为', output_filename)
            wordcloud.to_file(output_filename)
def main(input_filename):
    content = '\n'.join([line.strip()
                        for line in codecs.open(input_filename, 'r', 'utf-8')
                        if len(line.strip()) > 0])
    # 读取stopwords_filename对应的停用词文件 逐行获得停用词
    stopwords = set([line.strip()
                    for line in codecs.open(stopwords_filename, 'r', 'utf-8')])

    segs = jieba.cut(content)#用jieba对内容进行分词
    words = []
    for seg in segs:
        word = seg.strip().lower()
        if len(word) > 1 and word not in stopwords:
            words.append(word)#去掉前后空格，转换为小写，去掉停用词，然后加入到words列表中

    words_df = pandas.DataFrame({'word':words})#将words列表转换为pandas的DataFrame格式
    words_stat = words_df.groupby(by=['word']).size().reset_index(name='number')#按照word列进行分组，然后统计每组的数量
    words_stat = words_stat.sort_values(by="number",ascending=False)#排序

    print( '不同词语的数量 =', len(words_stat))

    input_prefix = input_filename
    if input_filename.find('.') != -1: # 如果文件名中有. 则取.之前的部分 获得文件名的前缀
        input_prefix =input_filename.split('.')[-2]#[:-1]表示从列表的开始一直到倒数第一个元素（不包括倒数第一个元素）

    for file in listdir(template_dir):
        if file[-4:] != '.png' and file[-4:] != '.jpg':
            continue
        background_picture_filename = join(template_dir, file)#获得所有以.jpg或.png结尾的文件，存进background_picture_filename
        if isfile(background_picture_filename):#确认是否是文件
            prefix = file.split('.')[0]#图片名字的前缀
            bimg=imageio(background_picture_filename)
            # 直接用WordCloud函数 传入字体路径、背景颜色、遮罩图片、最大字体大小、随机状态
            wordcloud=WordCloud(font_path=font_filename,background_color='white',mask = bimg,max_font_size=600,random_state=100)
            # 用fit_words函数传入words_stat的前4000个元素，iterrows()返回一个迭代器，每次迭代返回一个元组，元组的第一个元素是行索引，第二个元素是Series
            #index=false表示不返回行索引
            wordcloud=wordcloud.fit_words(dict(words_stat.head(4000).itertuples(index=False)))

            bimgColors=ImageColorGenerator(bimg)#把图片的颜色存入bimgColors
            wordcloud.recolor(color_func=bimgColors)#对词云进行着色
#输出路径为图片名字的前缀+输入文件名字的前缀+.png
            output_filename = prefix + '_' + input_prefix + '.png'
            print( '保存路径为', output_filename)
            wordcloud.to_file(output_filename)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        # 如果第二个参数是输入的文件名 则把文件名传入main函数
        main(sys.argv[1])
    else:
        while True:
            text = input('请输入文本内容：')
            if text == 'exit':
                break
            generate_by_text(text)



