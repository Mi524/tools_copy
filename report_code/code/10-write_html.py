from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time 

driver = webdriver.Chrome(r"D:\Download\chromedriver.exe")

driver.get('http://bpm.vivo.xyz/PortalNew/Portal/Index')

user_name = driver.find_element_by_name("txtUserName")
pass_word = driver.find_element_by_name("txtPassword")
btn_login = driver.find_element_by_name("btnLogin")

user_name.clear()
pass_word.clear()
user_name.send_keys("11106156")
pass_word.send_keys("2015*youseeme")

btn_login.click()

#等待进入页面
time.sleep(3)
#进入模块,固定的ID
driver.get("http://bpm.vivo.xyz/PortalNew/DocView/Index?c=5ceacd8af0704acc9ca28cafdb216cde")

time.sleep(1)
#进入报告页面, 应该是固定了唯一编码
report_page_url = "http://bpm.vivo.xyz/PZGL/HWPZBG?Message=wVz6Vc59L3q4xM2ObjK3Xyf%2ARUbNRC328yjoUvWisrnt57H8fXbp5YA1S_pw90yKy67nmW9bgw_d9RnADXJh7ZsQrnTND9dswAUC30r4rwAz6butAjGFPZhUWoavO7Oruuw0zClFtHRXF6MohiOEBQbc3029zR_tnOvPNJctdLl_DLtUokl3_tEMCsArUH_Wjjdv_BIqSUr%2Axv39jV2JKiYVzIrMFDMZUuDV_B5DgCH18E13MgpPzJWbsLsL1FbUrrF0_4_BuWP2dA_KQBoZ0DPp58_HwqaP1j0AdJ3faRFt%2AoJ_h7y%2APOv0GhsX8qhjaYr0BLISP4_qka1DT4CCqaPhnXPY7FgBgcQnrkSRqRI6zjcX30Jcev16pWgCK_Rgb5WMRxPrPessxAXUeuvnx2HDEliY5qECmUJ3nlMiV3ovuqOBHVSFVT4U9oyPjUwW"
driver.get(report_page_url)

time.sleep(2)

#加入两个新标签, 点击添加大标签选项 
plus_symbol = driver.find_element_by_class_name("fck-tool-btn")
plus_symbol.click()
time.sleep(2)
plus_symbol.click()
time.sleep(2)

#修改三个页面Tag的名称,通过xpath定位, tag1,tag2,tag3 分别对应： 概述，1.vivo整体负向口碑，2.vivo与竞品负向口碑对比
tag1 = driver.find_element_by_xpath('//*[@id="BFC_MainBody"]/div/div/div[1]/div[3]/ul/li[1]')
tag2 = driver.find_element_by_xpath('//*[@id="BFC_MainBody"]/div/div/div[1]/div[3]/ul/li[2]')
tag3 = driver.find_element_by_xpath('//*[@id="BFC_MainBody"]/div/div/div[1]/div[3]/ul/li[3]')

#JS方式修改标签名称
driver.execute_script("var elem = document.getElementsByClassName('fck-tabs-title'); elem[0].innerHTML='概述'", tag1)
time.sleep(2)
driver.execute_script("var elem = document.getElementsByClassName('fck-tabs-title'); elem[1].innerHTML='1.vivo整体负向口碑'", tag2)
time.sleep(2)
driver.execute_script("var elem = document.getElementsByClassName('fck-tabs-title'); elem[2].innerHTML='2.vivo与竞品负向口碑对比'", tag3)

time.sleep(1)
#进入第一个页面,将固定的部分写入
tag1.click()

edit_page1 = driver.find_element_by_id("ueditor_0")
#以下是在编辑页面内部的html (编辑部分是另一个<!doctype html>)
edit_body = edit_page1.find_element_by_xpath('/html/body')

def replace_excape(text):
	for c in '\'\"':
		text = text.replace(c,"\\" + c)
	return text 

with open(r'html\tag1.html','r',encoding='utf-8') as tag1_html:
	tag1_content = tag1_html.read()

script_text = """var elem = document.GetElementByTagName('p'); 
				 elem.insertAdjacentHTML('afterend','{}');
				 """.format(tag1_content)

script_text =  replace_excape(script_text)

driver.execute_script(script_text,edit_body)

#进入第二个页面, 先打开EXCEL将图片贴到框内，然后获取图片的链接
time.sleep(5)
driver.close()
driver.quit()
exit()

#鼠标单击第一行
first_edit_line.click()

