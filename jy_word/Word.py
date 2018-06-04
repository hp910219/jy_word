#! /usr/bin/env python
# coding: utf-8

import base64
import requests
import re
import traceback
import os


__author__ = 'huohuo'

contentType = "application/vnd.openxmlformats-package.relationships+xml"
schemas_mic_office = 'http://schemas.microsoft.com/office/word/'
urn = 'urn:schemas-microsoft-com'
schemas_mic_office_2010 = '%s/%d' % (schemas_mic_office, 2010)
schemas_mic_office_2006 = '%s/%d' % (schemas_mic_office, 2006)

schemas_open = 'http://schemas.openxmlformats.org'
schemas_open_2006 = '%s/officeDocument/%d'% (schemas_open, 2006)
schemas_open_draw_2006 = '%s/drawingml/%d'% (schemas_open, 2006)
schemas_open_pack_2006 = '%s/package/%d/relationships'% (schemas_open, 2006)


class JYFile:

    def __init__(self):
        self.__description__ = '文件相关， 包括读文件，写文件， 下载文件'

    def read(self, file_path, **kwargs):
        if not os.path.exists(file_path):
            return None
        read_type = 'r'
        if file_path.endswith('.png') or file_path.endswith('.jpg'):
            read_type = 'rb'
        if 'read_type' in kwargs:
            read_type = kwargs['read_type']
        f = open(file_path, read_type)
        text = f.read()
        f.close()
        return text

    def write(self, file_path, data):
        f = open(file_path, "w")
        f.write(data)
        f.close()

    def download(self, pkg_parts, file_name):
        try:
            temp_data = self.read("demo.xml")
            temp_data = temp_data.replace('<pkg:part id="pkg_parts"></pkg:part>', pkg_parts)
            self.write(file_name, temp_data)
            return 'success'
        except:
            message = traceback.format_exc()
            traceback.print_exc()
            return message


class Paragraph:
    def __init__(self):
        self.test = 'hello word'

    def write(self, pPr='', run='', bm_name=''):
        if pPr == '':
            pPr = self.set()
        para = '<w:p w:rsidR="008059BD" w:rsidRPr="008059BD" w:rsidRDefault="008059BD" w:rsidP="008059BD">' + pPr
        if bm_name != '':
            para += self.bookmart('Start', bm_name=bm_name)
            para += self.bookmart('End')
        para += run
        para += '</w:p>'
        return para

    def set(self, spacing=[0, 0], line=19.2, rule='exact', ind=[0, 0], jc='left',
            sect_pr='', outline=0, keepNext='', **kwargs):
        sss = ['before', 'after']
        w_spacing = '<w:spacing w:line="%d" ' % (int(line * 20))
        for i in range(len(sss)):
            if spacing[i] != 0:
                w_spacing += 'w:%s="%d" w:%sLines="%d" ' % (
                    sss[i], int(spacing[i] * 312), sss[i], int(spacing[i] * 100))
        w_spacing += 'w:lineRule="%s"/>' % rule
        if outline != 0:  # 大纲级别
            w_spacing += '<w:outlineLvl w:val="%d"/>' % outline

        if ind[0] == 'hanging':
            ind_str = '<w:ind w:left="%d" w:%sChars="%d" w:%s="%d"/>' % (ind[1] * 240, ind[0], ind[1] * 100, ind[0], ind[1] * 240)
        elif ind[0] == 'firstLine':
            ind_str = '<w:ind w:%sChars="%d" w:%s="%d"/>' % (ind[0], ind[1] * 100, ind[0], ind[1] * 220)
        elif ind == [0, 0]:
            ind_str = ''
        else:
            iii = ['left', 'right']
            ind_str = '<w:ind '
            for i in range(0, len(iii)):
                if (ind[i]) != 0:
                    if type(ind[i]) == str:
                        ind_str += 'w:%s="%d"' % (iii[i], int(float(ind[i].split("cm")[0]) * 567))
                    else:
                        ind_str += 'w:%sChars="%d" w:%s="%d"' % (iii[i], int(ind[i] * 100), iii[i], int(ind[i] * 210))
            ind_str += '/>'
        pStyle = ''
        if 'pStyle' in kwargs:
            pStyle = '<w:pStyle w:val="%s"/>' % kwargs['pStyle']
            if spacing == [0, 0]:
                w_spacing = ''
        pPr = '<w:pPr>%s%s%s<w:jc w:val="%s"/>%s%s' % (keepNext, w_spacing, ind_str, jc, sect_pr, pStyle)
        if 'tabs' in kwargs:
            tabs = kwargs['tabs']
            pPr += self.set_tabs(tabs[0], tabs[1], tabs[2])
        if 'shade' in kwargs:
            pPr += '<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % kwargs['shade']
        pPr += '</w:pPr>'
        return pPr

    def bookmart(self, bm_type='Start', bm_id=1, bm_name=''):
        if bm_name != '':
            bm_name = ' w:name="_Toc%s"' % bm_name
        book = '<w:bookmark%s w:id="%d"%s/>' % (bm_type, bm_id, bm_name)
        return book

    def tabs(self, pStyle='', pos="9736"):
        if pStyle != '':
            pStyle = '<w:pStyle w:val="%s"/>' % pStyle
        tabs = self.set_tabs(pos=pos)
        r = Run()
        run = r.text('', 11)
        pPr = '<w:pPr>%s%s%s</w:pPr>' % (pStyle, tabs, run)
        return pPr

    def set_tabs(self, val="right", leader="dot", pos="9736"):
        tabs = '<w:tabs><w:tab w:val="%s" w:leader="%s" w:pos="%s"/></w:tabs>' % (val, leader, pos)
        return tabs

    def set_pBdr(self, val='none', sz=0, space=0, color='auto'):
        pBdr = '<w:pBdr><w:bottom w:val="%s" w:sz="%d" w:space="%d" w:color="%s"/></w:pBdr>' % (val, sz, space, color)
        return pBdr

    def write_jy(self, contents_str, title, weight=0, spacing=[1.5, 0], para_space=[0, 0], ind=[0, 0]):
        r = Run()
        init = ""
        if title != "":
            init = self.h5(title, ind=ind)
        else:
            if contents_str == "":
                return ""
        if str(contents_str) in ["无", 'None', '', [], None]:
            return init + self.write(self.set(ind=ind), run=r.text(u'暂无数据'))
        if type(contents_str) == list:
            contents = contents_str
        else:
            contents = contents_str.split("\n")
        if title == "参考文献":
            if len(contents) > 10:
                contents = contents[:10]
        for i in range(0, len(contents)):
            if title == "参考文献":
                txt = str(i + 1) + ". " + str(contents[i]["literature_author"].split(",")[0])
                txt += ". et, al" + " (" + str(contents[i]["published_year"]) + ")."
                txt += str(contents[i]["literature_title"])
                txt += str(contents[i]["literature_source"]) + "."
                txt = txt.replace("<", "&lt;").replace(">", "&gt;")
            else:
                txt = contents[i]
                txt = txt.replace("<", "&lt;").replace(">", "&gt;")
            # if txt != '':
            init += self.write(self.set(spacing=para_space, ind=ind), run=r.text(txt))
        return init

    def write_figures(self, figures=[], line=19.2, ind=[12, 7], cx=1.59, cy=0.4, posOffset=[-21, 0.25]):
        r = Run()
        init = ""
        for f in figures:
            init += self.write(self.set(line=line, ind=ind), r.text(f['text']) + r.picture(cx, cy, f['rId'],
                                                                                           relativeFrom=['rightMargin',
                                                                                                         'paragraph'],
                                                                                           posOffset=posOffset))
        return init

    def h5(self, text, size=11, spacing=[1.5, 0], weight=0, ind=[0, 0], line=18, jc='left', outline=4, family='', family_en='', bm_name=''):
        r = Run()
        if family != '':
            r.family = family
        if family_en != '':
            r.family_en = family_en
        return self.write(self.set(spacing=spacing, line=line, rule='auto', outline=outline, ind=ind, jc=jc),
                          r.text(text, size, weight=weight), bm_name)

    def h4(self, text='', size=11, spacing=[1.5, 0], weight=1, ind=[0, 0], line=24, runs='', family='', family_en='', bm_name=''):
        r = Run()
        if family != '':
            r.family = family
        if family_en != '':
            r.family_en = family_en
        run = r.text(text, size=size, weight=weight) + runs
        return self.write(self.set(spacing=spacing, line=line, rule='auto', outline=3, ind=ind), run, bm_name)

    def h3(self, text, run='', before=0, after=0, size=11, left=0, right=0, jc='center', family='', family_en=''):
        r = Run()
        if family != '':
            r.family = family
        if family_en != '':
            r.family_en = family_en
        spacing = [before, after]
        ind = [left, right]
        pPrr = self.set(spacing=spacing, line=24, rule='auto', outline=2, jc=jc, ind=ind)
        r1 = r.text(text, size)
        if run != '':
            r1 = run
        para = self.write(pPrr, r1)
        return para

    def h2(self, text, before=0, after=0, size=28.5, family='', family_en=''):
        r = Run()
        if family != '':
            r.family = family
        if family_en != '':
            r.family_en = family_en
        spacing = [before, after]
        pPrr = self.set(spacing=spacing, line=43.4, outline=1, jc='center')
        para = self.write(pPrr, r.text(text, size))
        return para

    def h2en(self, text, before=0, after=0, size=11.5, family='', family_en=''):
        r = Run()
        if family != '':
            r.family = family
        if family_en != '':
            r.family_en = family_en
        spacing = [before, after]
        pPrr = self.set(spacing=spacing, line=26.1, outline=1, jc='center')
        para = self.write(pPrr, r.text(text, size))
        return para

    def null_data(self, title=''):
        r = Run()
        text = '暂无数据'
        if title == "predict_consequences":
            text = '暂未发现危险变异'
        para = self.write(run=r.text(text))
        return para


class HyperLink:
    def __init__(self):
        self.a = ''

    def write(self, index, content, page):
        r = Run()
        text = '<w:hyperlink w:anchor="_Toc%d" w:history="1">' % index
        text += r.style(content)
        text += r.tab()
        text += r.fldChar('begin')
        text += r.instr_text(' PAGEREF _Toc%d \h ' % index, space=True)
        text += r.text('')
        text += r.fldChar()
        text += r.text(page)
        text += r.fldChar('end')
        text += '</w:hyperlink>'
        return text


class SDT:
    def __init__(self):
        self.a = ''

    def write(self):
        r = Run()
        text = r.fldChar('begin')
        text += r.instr_text('PAGE   \* MERGEFORMAT')
        text += r.fldChar('separate')
        text += r.text(1, noProof=True, lang='zh-CN')
        text += r.fldChar('end')
        p = Paragraph()
        para = p.write(p.set(pStyle='a5', jc='center'), text)
        sdt = '<w:sdt>'
        sdt += '''
                <w:sdtPr>
                    <w:id w:val="-971206286"/>
                    <w:docPartObj>
                        <w:docPartGallery w:val="Page Numbers (Bottom of Page)"/>
                        <w:docPartUnique/>
                    </w:docPartObj>
                </w:sdtPr>
                <w:sdtEndPr/>
            '''
        sdt += '<w:sdtContent>%s</w:sdtContent>' % para
        sdt += '</w:sdt>'
        # sdt += p.write(p.set(pStyle='a5', jc='center'))
        return sdt


class Run:
    def __init__(self):
        self.test = 'hello word'
        self.familyTheme = 'minorEastAsia'
        self.family_en = 'Times New Roman'
        self.family = ''

    def text(self, content, size=11, weight=0, underline='', space=False, wingdings=False, windChar='F09E',
             vertAlign='', lastRender=False, br='', color='', italic=False, fill='', rStyle=False, rStyleVal='', szCs=0, lang='', noProof=False):
        rFonts = '<w:rFonts w:ascii="' + self.family_en
        if self.family == '':
            rFonts += '" w:eastAsiaTheme="' + self.familyTheme
        else:
            rFonts += '" w:eastAsia="%s' % self.family
        rFonts += '" w:hAnsi="' + self.family_en + '" w:cs="Times New Roman"/>'
        sz = '<w:sz w:val="%d"/>' % int(size * 2)
        if szCs != 0:
            sz += '<w:szCs w:val="%d"/>' % int(szCs)
        uuu = ''
        weight_str = ""
        lastRendered = ''
        if weight != 0:
            weight_str = "<w:b/><w:bCs/>"
        if underline != '':
            uuu = '<w:u w:val="%s"/>' % underline
        if color != '':
            color = '<w:color w:val="%s"/>' % color
        if vertAlign == 'top':
            vertAlign = '<w:vertAlign w:val="superscript"/>'
        elif vertAlign == 'bottom':
            vertAlign = '<w:vertAlign w:val="subscript"/>'
        if italic:
            italic = '<w:i/>'
        else:
            italic = ''
        if rStyle:
            sz += '<w:rStyle w:val="%s"/>' % rStyleVal
        rPr = '<w:rPr>' + rFonts + weight_str + italic + uuu + sz + vertAlign + color
        if noProof:
            rPr += '<w:noProof/>'
        if lang != '':
            rPr += '<w:lang w:val="zh-CN"/>'
        rPr += '</w:rPr>'
        wt = ''
        if content != '':
            space1 = ''
            if space:
                space1 = ' xml:space="preserve"'
            wt = '<w:t%s>%s</w:t>' % (space1, content)
        if lastRender:
            lastRendered = '<w:lastRenderedPageBreak/>'
        wingdings1 = ''
        if wingdings:
            wingdings1 = '<w:sym w:font="Wingdings" w:char="%s"/>' % windChar
        shd = ''
        if fill != '':
            shd = '<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % fill
        r = '<w:r w:rsidRPr="008059BD">%s%s%s%s%s</w:r>' % (rPr, wingdings1, lastRendered, shd, wt)
        if br == 'column':
            r += '<w:r w:rsidR="003334DE"><w:br w:type="column"/></w:r>'
        return r

    def style(self, text, val='af8'):
        r = '<w:r><w:rPr><w:rStyle w:val="%s"/><w:rFonts w:eastAsiaTheme="%s"/></w:rPr><w:t>%s</w:t></w:r>' % (val, self.familyTheme, text)
        return r

    def br(self, br_type='column'):
        r = '<w:r w:rsidR="003334DE"><w:br w:type="%s"/></w:r>' % br_type
        return r

    def picture(self, cx=0, cy=0, rId='', relativeFrom=['column', 'paragraph'], posOffset=[0, 0], align=['', ''],
                wrap='tight', text_wrapping='anchor'):
        p = ['positionH', 'positionV']
        postition = ''
        srcRect = ''
        bwMode = ''
        picPr = '<pic:cNvPicPr><a:picLocks noChangeAspect="1" noChangeArrowheads="1"/></pic:cNvPicPr>'
        noFill = '<a:noFill/>'
        wp14 = ''
        framePr = '<wp:cNvGraphicFramePr>'
        framePr += '<a:graphicFrameLocks noChangeAspect="1" xmlns:a="%s/main"/>' % schemas_open_draw_2006
        framePr += '</wp:cNvGraphicFramePr>'
        if wrap == 'tight':
            wrappp = '''
            <wp:wrapTight wrapText="bothSides">
                <wp:wrapPolygon edited="0">
                    <wp:start x="4719" y="0"/>
                    <wp:lineTo x="3267" y="2919"/>
                    <wp:lineTo x="2904" y="9341"/>
                    <wp:lineTo x="0" y="14011"/>
                    <wp:lineTo x="0" y="21016"/>
                    <wp:lineTo x="1089" y="21016"/>
                    <wp:lineTo x="1452" y="21016"/>
                    <wp:lineTo x="3630" y="18681"/>
                    <wp:lineTo x="21418" y="15762"/>
                    <wp:lineTo x="21418" y="2919"/>
                    <wp:lineTo x="7261" y="0"/>
                    <wp:lineTo x="4719" y="0"/>
                </wp:wrapPolygon>
            </wp:wrapTight>'''
            framePr = '<wp:cNvGraphicFramePr/>'
            picPr = '<pic:cNvPicPr/>'
        elif wrap == 'undertext':
            wrappp = '<wp:wrapNone/>'
            srcRect = '<a:srcRect/>'
            bwMode = ' bwMode="auto"'
            noFill = ''
            wp14 = '<wp14:sizeRelH relativeFrom="page"><wp14:pctWidth>0</wp14:pctWidth></wp14:sizeRelH>'
            wp14 += '<wp14:sizeRelV relativeFrom="page"><wp14:pctHeight>0</wp14:pctHeight></wp14:sizeRelV>'
        else:
            wrappp = ''

        for i in range(0, len(p)):
            postition += '<wp:%s relativeFrom="%s">' % (p[i], relativeFrom[i])
            if align[i] != '':
                postition += '<wp:align>%s</wp:align></wp:%s>' % (align[i], p[i])
            else:
                postition += '<wp:posOffset>%d</wp:posOffset></wp:%s>' % (int(posOffset[i] * 359410), p[i])
        run = '<w:r><w:drawing><wp:%s distT="0" distB="0" ' % text_wrapping
        extent_r = 9525
        if text_wrapping == 'anchor':
            run += 'distL="114300" distR="114300" simplePos="0" relativeHeight="251658240" behindDoc="1" locked="0" layoutInCell="1" allowOverlap="1">'
            run += '<wp:simplePos x="0" y="0"/>'
            run += postition
        elif text_wrapping == 'inline':
            run += 'distL="0" distR="0">'
            wrappp = ''
            extent_r = 0
            noFill += '<a:ln w="9525"><a:noFill/><a:miter lim="800000"/><a:headEnd/><a:tailEnd/></a:ln>'
        run += '<wp:extent cx="%d" cy="%d"/>' % (int(cx * 359410), int(cy * 359410))
        run += '<wp:effectExtent l="0" t="0" r="%d" b="0"/>%s<wp:docPr id="1" name="图片 1"/>' % (extent_r, wrappp)
        run += framePr
        run += '<a:graphic xmlns:a="%s/main">' % schemas_open_draw_2006
        run += '<a:graphicData uri="%s/picture">' % schemas_open_draw_2006
        run += '<pic:pic xmlns:pic="%s/picture"><pic:nvPicPr><pic:cNvPr id="0" name=""/>' % schemas_open_draw_2006
        run += picPr

        run += '</pic:nvPicPr><pic:blipFill>'
        run += '<a:blip r:embed="%s"' % rId
        if text_wrapping != 'inline':
            run += ' cstate="print"><a:extLst><a:ext uri="{28A0092B-C50C-407E-A947-70E740481C1C}">'
            run += '<a14:useLocalDpi val="0" xmlns:a14="http://schemas.microsoft.com/office/drawing/2010/main"/>'
            run += '</a:ext></a:extLst></a:blip>'
            run += srcRect
            fill_type = '<a:stretch><a:fillRect/></a:stretch>'
        else:
            run += '/>'
            fill_type = '<a:srcRect/><a:stretch><a:fillRect/></a:stretch>'
        run += '%s</pic:blipFill>' % fill_type
        run += '<pic:spPr%s>' % bwMode
        run += '<a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm>' % (int(cx * 359410), int(cy * 359410))
        run += '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>%s</pic:spPr>' % noFill
        run += '</pic:pic></a:graphicData></a:graphic>%s' % wp14
        run += '</wp:%s></w:drawing></w:r>' % text_wrapping
        return run

    def instr_text(self, text='', space=False):
        space1 = ''
        if space:
            space1 = ' xml:space="preserve"'
        if text == '1-3':
            text = 'TOC \o "1-3" \h \u '
        r1 = '<w:r><w:instrText%s>%s</w:instrText></w:r>' % (space1, text)
        return r1

    def fldChar(self, fldCharType='separate'):
        r1 = '<w:r><w:fldChar w:fldCharType="%s"/></w:r>' % fldCharType
        return r1

    def tab(self):
        r1 = '<w:r><w:rPr><w:rFonts w:eastAsiaTheme="%s"/></w:rPr><w:tab/></w:r>' % self.familyTheme
        return r1


class Set_page:
    def __init__(self):
        self.test = 'test'

    def set_page(self, sign='', type='', cols=1, header='', footer='', space=425, pgNumType_s=-1, page_size=[21, 29.7], page_margin=[2.54, 3, 2.54, 3, 2, 1.47], orient=""):
        mar = ['top', 'right', 'bottom', 'left', 'header', 'footer']
        a = '<w:sectPr w:rsidR="008059BD" w:rsidSect="008059BD">'
        # <w:pgSz w:w="16838" w:h="11906" w:orient="landscape"/>
        if type == 'continuous':
            a += '<w:type w:val="continuous"/>'
        if header != '':
            a += '<w:headerReference w:type="default" r:id="%s"/>' % header
        if footer != '':
            a += '<w:footerReference w:type="default" r:id="%s"/>' % footer
        pg_sz = '<w:pgSz w:w="%d" w:h="%d"/>' % (int(page_size[0] * 567), int(page_size[1] * 567))
        if orient == 'landscape':
            pg_sz = '<w:pgSz w:w="%d" w:h="%d" w:orient="%s"/>' % (int(page_size[1] * 567), int(page_size[0] * 567), orient)
        a += pg_sz
        pgMar = '<w:pgMar'
        for i in range(0, len(mar)):
            pgMar += ' w:%s="%d"' % (mar[i], int(page_margin[i] * 567))
        a += pgMar + ' w:gutter="0"/>'
        if pgNumType_s > 0:
            a += '<w:pgNumType w:start="%d"/>' % pgNumType_s
        if cols == 1:
            a += '<w:cols w:space="%d"/>' % space
        elif cols == 2:
            a += '<w:cols w:num="2" w:space="%d"/>' % space
        a += '<w:docGrid w:type="lines" w:linePitch="312"/></w:sectPr>'

        return a


class Table:
    def __init__(self):
        self.test = ''

    def write(self, trs='', ws=[], tblBorders=['top', 'left', 'bottom', 'right']):
        tblPr = '<w:tblPr><w:tblW w:w="%d" w:type="dxa"/><w:jc w:val="center"/>' % sum(ws)
        tblPr += '<w:tblBorders>'
        for b in tblBorders:
            tblPr += '<w:%s w:val="single" w:sz="4" w:space="0" w:color="auto"/>' % b
        tblPr += '</w:tblBorders>'
        tblPr += '<w:tblLayout w:type="fixed"/>'
        tblPr += '''<w:tblLook w:val="0000" w:firstRow="0" w:lastRow="0" w:firstColumn="0" w:lastColumn="0" w:noHBand="0" w:noVBand="0"/>
        </w:tblPr>'''
        tblGrid = '<w:tblGrid>'
        for w in ws:
            tblGrid += '<w:gridCol w:w="%d"/>' % w
        tblGrid += '</w:tblGrid>'
        table = '<w:tbl>' + tblPr + tblGrid + trs + '</w:tbl>'
        return table

    def write_jy(self, trsss, tcBorders=['top', 'bottom'], ws=[], jc='center', before=0, after=0, sign='', gene=None, tblBorders=['top', 'left', 'bottom', 'right'], theadColor='auto', thBorders=['top', 'bottom'], jc2=''):
        tr = Tr()
        tc = Tc()
        p = Paragraph()
        r = Run()
        if len(trsss) == 0:
            return p.null_data()
        trs = ''
        pPr = p.set(jc=jc, spacing=[before, after])
        for k in range(len(trsss)):
            tr2 = trsss[k]
            if 'sign' in tr2:
                trPr = tr.set('<w:cantSplit/>')
                if 'trHeight' in tr2:
                    trPr = tr.set('<w:cantSplit/>', tr2['trHeight'])
                if tr2['sign'] == 'th1':
                    trs += tr.write(set=trPr, tcs=tc.write(p.write(run=r.text(tr2['text'][0], weight=1)),
                                                           tc.set(w=sum(ws), tcBorders=tcBorders, gridSpan=4)))
                if tr2['sign'] == 'th1-1':
                    para = p.write(run=r.text(tr2['text'][0].split("\n")[0], weight=1))
                    if "\n" in tr2['text'][0]:
                        for i in range(1, len(tr2['text'][0].split("\n"))):
                            para += p.write(run=r.text(tr2['text'][0].split("\n")[i]))
                    trs += tr.write(set=trPr, tcs=tc.write(para, tc.set(w=sum(ws), tcBorders=tcBorders, gridSpan=4,
                                                                        vAlign='top')))
                if tr2['sign'] == 'th2':
                    tcs = tc.write(p.write(pPr, run=r.text(tr2['text'][0])),
                                   tc.set(w=sum(ws[:1]), tcBorders=tcBorders, gridSpan=1))
                    run = r.text(tr2['text'][1])
                    tcs += tc.write(p.write(pPr, run=run), tc.set(w=sum(ws[1:]), tcBorders=tcBorders, gridSpan=3))
                    trs += tr.write(set=trPr, tcs=tcs)
            else:
                tcs2 = ''
                size = 10
                weight = 0
                fill= 'auto'
                tcBorders1 = tcBorders

                if sign == '':
                    if k == 0:
                        size = 11
                        weight = 1
                        fill = theadColor
                        tcBorders1 = thBorders
                for i in range(len(tr2['text'])):
                    if tr2['text'][i] == 'picture':
                        tcs2 += tc.write(p.write(pPr, run=tr2['picture']), tc.set(w=ws[i], tcBorders=tcBorders))
                    else:
                        italic = False
                        if k > 0 and gene != None and i == gene:
                            italic = True
                        run = ''
                        if tr2['text'][i] == '1000G频率':
                            run = r.text('1000G', size=size, italic=italic, weight=weight)
                            run += r.text('', wingdings=True, windChar='F040', vertAlign='top')
                            run += r.text('频率', size=size, italic=italic, weight=weight)
                        else:
                            run = r.text(tr2['text'][i], size=size, italic=italic, weight=weight)
                        if i == 0 or k == 0:
                            jc1 = jc
                        else:
                            jc1 = jc if jc2 == '' else jc2
                        pPr = p.set(jc=jc1, spacing=[before, after])
                        tcs2 += tc.write(
                            p.write(pPr, run),
                            tc.set(w=ws[i], tcBorders=tcBorders1, fill=fill))
                trs += tr.write(tcs2)
        return self.write(trs, ws=ws, tblBorders=tblBorders)

    def write_jy1(self, trsss, ws, table_borders=['top', 'left', 'bottom', 'right'], tc_borders=['top', 'bottom'], sign='', gene=None,  th_color='auto', th_borders=['top', 'bottom'], th_size=10, tc_size=10, th_weight=1, tc_weight=0, tc_color='auto', th_pPr='', tc_pPr=''):
        tr = Tr()
        tc = Tc()
        p = Paragraph()
        r = Run()
        if len(trsss) == 0:
            return p.null_data()
        trs = ''
        for k in range(len(trsss)):
            tr2 = trsss[k]
            gridSpan = [0] * len(ws)
            ws1 = ws
            vAlign = 'center'
            trPr = ''
            tcs2 = ''
            size = tc_size
            weight = tc_weight
            fill = tc_color
            tcBorders1 = tc_borders
            cantSplit = ''
            pPr = tc_pPr
            if k == 0:
                size = th_size
                weight = th_weight
                fill = th_color
                tcBorders1 = th_borders
                pPr = th_pPr
            if 'trHeight' in tr2:
                trPr = tr.set(tr2['trHeight'])
            if 'sign' in tr2:
                gridSpan = [len(ws)]
                ws1 = [sum(ws)]
                vAlign = 'center'
                cantSplit = '<w:cantSplit/>'
                if tr2['sign'] == 'th1-1':
                    vAlign = 'top'
                if tr2['sign'] == 'th2':
                    gridSpan = [1, len(ws) - 1]
                    ws1 = [ws[0], ws[1:]]
            if 'trHeight' in tr2:
                trPr = tr.set(cantSplit, tr2['trHeight'])
            for i in range(len(tr2['text'])):
                if tr2['text'][i] == 'picture':
                    tcs2 += tc.write(p.write(pPr, run=tr2['picture']), tc.set(w=ws[i], tcBorders=tc_borders))
                else:
                    text = tr2['text'][i]
                    if type(text) == int:
                        text = str(text)
                    texts = text.split('\n')
                    italic = False
                    if k > 0 and gene != None and i == gene:
                        italic = True
                    if sign != '' and sign in texts[0]:
                        texts0 = texts[0].split(sign)
                        run = r.text(texts0[0], size=size, italic=italic, weight=weight)
                        run_sign = r.text(sign, vertAlign='top', size=size)
                        if sign == 'F040':
                            run_sign = r.text('', wingdings=True, windChar='F040', vertAlign='top')
                        run += run_sign
                        if len(texts0) > 1:
                            run += r.text(texts0[1], size=size, italic=italic, weight=weight)
                    else:
                        texts1 = texts[0].split('indextop')
                        if len(texts1) > 1:
                            run = r.text(texts1[0], size=size, italic=italic, weight=weight, vertAlign='top')
                            run += r.text(texts1[1], size=size, italic=italic, weight=weight)
                        else:
                            run = r.text(texts1[0], size=size, italic=italic, weight=weight)
                    para = p.write(pPr, run=run)
                    for t in texts[1:]:
                        para += p.write(pPr, r.text(t))
                    tcs2 += tc.write(para, tc.set(w=ws1[i], tcBorders=tcBorders1, gridSpan=gridSpan[i], vAlign=vAlign, fill=fill))
            trs += tr.write(set=trPr, tcs=tcs2)
        return self.write(trs, ws=ws, tblBorders=table_borders)


class Tr:
    def __init__(self):
        self.test = ''

    def write(self, set='', tcs=''):
        tr = '<w:tr w:rsidR="008059BD" w:rsidRPr="008059BD" w:rsidTr="008059BD">' + set + tcs + '</w:tr>'
        return tr

    def set(self, cantSplit='', trHeight=0):
        hhhh = ''
        if trHeight != 0:
            hhhh = '<w:trHeight w:hRule="exact" w:val="%d"/>' % trHeight
        trPr = '<w:trPr>%s%s<w:jc w:val="center"/></w:trPr>' % (cantSplit, hhhh)
        return trPr


class Tc:
    def __init__(self):
        self.test = 'test'

    def write(self, paras='', tcPr=''):
        tc = '<w:tc>' + tcPr + paras + '</w:tc>'
        return tc

    def set(self, w=0, vMerge='', tcBorders=['top', 'bottom'], gridSpan=0, vAlign='center', color="auto", fill='auto'):
        # if w < 100:
        #     w = int(w * 567)
        #     print w
        tcBorders_str = ''
        if len(tcBorders) > 0:
            tcBorders_str = '<w:tcBorders>'
            for b in tcBorders:
                tcBorders_str += '<w:%s w:val="single" w:sz="4" w:space="0" w:color="%s"/>' % (b, color)
            tcBorders_str += '</w:tcBorders>'
        tcPr = '<w:tcPr><w:tcW w:w="%d" w:type="dxa"/>' % w
        if gridSpan != 0:
            tcPr += '<w:gridSpan w:val="%d"/>' % gridSpan
        tcPr += vMerge + tcBorders_str + '<w:shd w:val="clear" w:color="auto" w:fill="%s"/><w:vAlign w:val="%s"/></w:tcPr>' % (fill, vAlign)
        return tcPr


class Relationship:
    def __init__(self):
        self.none = 'none1'

    def write_rel(self, rId, type='image', target_name='', target_mode='', office='officeDocument'):
        if office == '':
            office = 'officeDocument'
        Type = '%s/%s/2006/relationships/%s' % (schemas_open, office, type)
        if type == 'image':
            target = 'media/%s.png' % rId
        elif type == 'theme':
            target = 'them1.xml'
        elif type in ['header', 'footer']:
            target = '%s.xml' % rId
        else:
            target = '%s.xml' % type
        if target_name != '':
            target = target_name
        target_mode1 = '' if target_mode == '' else ' TargetMode="%s"' % target_mode
        rel = '<Relationship Id="rId%s" Type="%s" Target="%s"%s/>' % (rId.capitalize(), Type, target, target_mode1)
        return rel

    def write_pkg(self, rId, url):
        pkg_part = '<pkg:part pkg:name="/word/media/%s.png" pkg:contentType="image/png" pkg:compression="store">' % (
            rId)
        pkg_part += '<pkg:binaryData>' + pic_b64encode(url, none=self.none) + '</pkg:binaryData></pkg:part>'
        return pkg_part

    def document_pkg_part(self, body):
        return self.about_page('document', '<w:body>%s</w:body>' % body, page_type='document', xml_data='document')

    def document_rels(self, rels, pkg_name="/word/_rels/document.xml", padding=256):
        pkg_part = '''
            <pkg:part pkg:name="%s.rels" pkg:contentType="%s" pkg:padding="%d">
                <pkg:xmlData>
                    <Relationships xmlns="%s">
                        %s
                    </Relationships>
                </pkg:xmlData>
            </pkg:part>''' % (pkg_name, contentType, padding, schemas_open_pack_2006, rels)
        return pkg_part

    def about_page(self, i, contents, page_type='footer', rels='', xml_data=''):
        pkg_part = '<pkg:part pkg:name="/word/%s.xml" ' % i
        if page_type == 'document':
            page_type += '.main'
        xml_name = ('%sr' %(page_type[0] + page_type[3])) if xml_data == '' else xml_data
        pkg_part += 'pkg:contentType="application/vnd.openxmlformats-officedocument.wordprocessingml.%s+xml">' % page_type
        pkg_part += '<pkg:xmlData><w:%s mc:Ignorable="w14 wp14" ' % (xml_name)
        xmlns = 'xmlns:wpc="%s/wordprocessingCanvas" ' % schemas_mic_office_2010
        xmlns += 'xmlns:mc="%s/markup-compatibility/2006" ' % schemas_open
        xmlns += 'xmlns:o="%s:office:office" ' % urn
        xmlns += 'xmlns:r="%s/relationships" ' % schemas_open_2006
        xmlns += 'xmlns:m="%s/math" ' % schemas_open_2006
        xmlns += 'xmlns:v="%s:vml" ' % urn
        xmlns += 'xmlns:wp14="%s/wordprocessingDrawing" ' % schemas_mic_office_2010
        xmlns += 'xmlns:wp="%s/drawingml/2006/wordprocessingDrawing" ' % schemas_open
        xmlns += 'xmlns:w10="%s:office:word" ' % urn
        xmlns += 'xmlns:w="%s/wordprocessingml/2006/main" ' % schemas_open
        xmlns += 'xmlns:w14="%s/wordml" ' % schemas_mic_office_2010
        xmlns += 'xmlns:wpg="%s/wordprocessingGroup" ' % schemas_mic_office_2010
        xmlns += 'xmlns:wpi="%s/wordprocessingInk" ' % schemas_mic_office_2010
        xmlns += 'xmlns:wne="%s/wordml" ' % schemas_mic_office_2006
        xmlns += 'xmlns:wps="%s/wordprocessingShape">' % schemas_mic_office_2010
        pkg_part += xmlns
        pkg_part += contents
        pkg_part += '</w:%s></pkg:xmlData></pkg:part>' % (xml_name)
        if rels != '':
            pkg_part += '<pkg:part pkg:name="/word/_rels/%s.xml.rels" pkg:contentType="%s">' % (i, contentType)
            pkg_part += '<pkg:xmlData><Relationships xmlns="%s">%s</Relationships></pkg:xmlData></pkg:part>' % (schemas_open_pack_2006, rels)
        return pkg_part

    def notes(self, note='endnote'):
        note_type = ['separator', 'continuationSeparator']
        content = ''
        for i in range(len(note_type)):
            content += '<w:%s w:type="%s" w:id="%d">' % (note, note_type[i], i-1)
            content += '<w:p w:rsidR="0035090B" w:rsidRDefault="0035090B"><w:r><w:%s/></w:r></w:p></w:%s>' % (note_type[i], note)
        rel_type = '%ss' % note
        return self.about_page(rel_type, content, rel_type, xml_data=rel_type)


def pic_b64encode(url, none='none1'):
    my_file = JYFile()
    if url.startswith('http://'):
        try:
            rq = requests.get(url)
            if rq.status_code == 200:
                content = rq.content
            else:
                content = None
        except:
            content = None
    else:
        content = my_file.read(url + '.png')
    if content is None:
        content = my_file.read('%s.png' % none)
    image_rb = base64.b64encode(content)
    return image_rb


def write_pkg_parts(rIds, urls, body,  none='none', show_page=True):
    relationship = Relationship()
    relationship.none = none
    p = Paragraph()
    relationshipss = []
    aa = [
        [
            ['1', 'officeDocument', 'word/document.xml'],
            ['2', 'core-properties', '/docProps/core.xml', '', 'package'],
            ['3', 'extended-properties', 'docProps/app.xml'],
            ['4', 'custom-properties', 'docProps/custom.xml'],
        ], [
            ['1', 'customXml', '../customXml/item1.xml'],
            ['2', 'customXml', '../customXml/item2.xml'],
            ['3', 'numbering'],
            ['4', 'styles'], ['5', 'stylesWithEffects'], ['6', 'settings'], ['7', 'webSettings'],
            ['8', 'footnotes'], ['9', 'endnotes'],
            ['19', 'hyperlink', 'http://www.hgvs.org/mutnomen/', 'External'],
            ['35', 'fontTable'], ['36', 'theme', 'theme/theme1.xml']
        ]
    ]
    for i in aa:
        relationships = ''
        for a in i:
            target_name = '' if len(a) < 3 else a[2]
            target_mode = '' if len(a) < 4 else a[3]
            relationships += relationship.write_rel(a[0], a[1], target_name, target_mode)
        relationshipss.append(relationships)
    pkg_parts = ''
    for i in range(len(rIds)):
        relationshipss[1] += relationship.write_rel(rIds[i])
        pkg_parts += relationship.write_pkg(rIds[i], urls[i])
    if show_page:
        sdt = SDT()
        footers_pkg = [sdt.write(), p.write(p.set(pStyle="a5"))]
        indexs = [1, 2]
        for index in indexs:
            footer_index = 'footer%d' % index
            pkg_parts += relationship.about_page(footer_index, footers_pkg[index-1])
            relationshipss[1] += relationship.write_rel(footer_index, 'footer')
    pkg_parts0 = relationship.document_rels(relationshipss[0], pkg_name='/_rels/', padding=512)
    pkg_parts0 += relationship.document_rels(relationshipss[1])
    pkg_parts0 += relationship.document_pkg_part(body)
    pkg_parts0 += pkg_parts
    pkg_parts0 += relationship.notes()
    pkg_parts0 += relationship.notes('footnote')
    return pkg_parts0


def write_cat(cat, index, para, pos='9736', spacing=[0, 0]):
    r = Run()
    p = Paragraph()
    hyperlink = HyperLink()
    run = ''
    if index == 453150345:
        run = r.fldChar('begin')
        run += r.instr_text('1-3', space=True)
        run += r.fldChar()
    run += hyperlink.write(index, cat[0], cat[2])
    para += p.write(p.set(pStyle=cat[3], tabs=['right', 'dot', pos], line=18, spacing=spacing, rule='auto'), run=run)
    index += 1
    return para, index


def str_except(data, key, text=u"无"):
    # key = 'name'
    # text = u"无"
    if data is None:
        return text
    text1 = text
    if key in data:
        if data[key] != None:
            if type(data[key]) == dict and key in data[key]:
                value = data[key][key]
            else:
                value = data[key]
            if value not in [None, '']:
                text1 = u'%s' % str(value)
    if text1 == 'N/A' and text != 'N/A':
        return text
    return text1


def str_length(contents):
    '''
    :param: contents: str
    汉字与大写字母占两位，其余占一位
    :return 字符串的在word中的占位
    '''
    ch_pattern = re.compile(u'[\u4e00-\u9fa5A-Z]+')
    match = ch_pattern.search(contents)
    n = len(contents)
    if match:
        a = ch_pattern.findall(contents)
        for i in a:
            n += len(i)
    return n
