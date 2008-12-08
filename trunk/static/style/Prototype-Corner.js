var Corner = {
     // ��־Բ��λ�õ����
    TOP_LEFT:     0x1 ,
    TOP_RIGHT:     0x2 ,
    BOTTOM_LEFT:   0x4 ,
    BOTTOM_RIGHT: 0x8 ,
    ALL:           0xf ,
   
     /**/ /* *******************************************************
    * target: ҪԲ�ǵ�Ŀ��Ԫ��
    * radius: Բ�ǵİ뾶��Ĭ��ֵΪ5
    * flags: Բ��λ�õ���������ϣ�Ĭ��ֵΪȫ��
    * backgroundColor: Բ�ǵı���ɫ��Ĭ��ֵΪĿ��Ԫ�صı���ɫ
    ******************************************************* */
     round: function (target, radius, flags, backgroundColor) {
         var t = $(target);
         var r = radius || 5 ;
         var f = flags || Corner.ALL;
         var c = Element.getStyle(t, 'backgroundColor');
         var b = backgroundColor || c;
       
         // ������IE��Ԫ����ʽΪFLOATʱ��Բ��DIV���Ϊ0��BUG
         var ft = Element.getStyle(t, ' float ');
         if (navigator.appVersion.match( / \bMSIE\b / ) && ft != 'none' && ! t.style.width) {           
            Element.setStyle(t, { width: Element.getWidth(t) + 'px' } );
        }
       
         // ����DIV������Ŀ��Ԫ�ص����ݼ��е�����
         var d = document.createElement('div');         
        d.innerHTML = t.innerHTML;
        t.innerHTML = '';       
       
         // ������DIV�ı���ɫΪĿ��Ԫ�صı���ɫ����Ŀ��Ԫ��Ϊ͸������
         Element.setStyle( d, { backgroundColor: c } );     
        Element.setStyle( t, { backgroundColor: 'transparent' } );     
       
         // ������DIV�ĸ߶�ΪĿ��Ԫ�صĸ߶�
         var h = t.style.height;
         var nh = 0 ;
         if (h) {
            Element.setStyle( d, { height: h } );
            nh = parseInt(h);
        }                   
       
         // ������DIV������
         var p = Element.getStyle(t, 'padding');
         if (p) {
            Element.setStyle( d, { padding: p } );           
            Element.setStyle( t, { padding: '0px 0px 0px 0px' } );
        }         
       
         // ����������DIV��Բ��DIV���ĵ�Ƭ�Σ���������ÿ������Ԫ����ʽ�������Ԫ��ʱ�ػ�ҳ�棬���Ч��
         var ds = document.createDocumentFragment();               
         var ls = null ;
         // ��������Բ��DIV
          if (f & (Corner.TOP_LEFT | Corner.TOP_RIGHT)) {
            ls = Corner._createRoundFragment(r, f, b , false );           
            ds.appendChild(ls);            
            nh += r;
        }       
       
        ds.appendChild(d);
       
         // �����ײ�Բ��DIV
          if (f & (Corner.BOTTOM_LEFT | Corner.BOTTOM_RIGHT)) {
            ls = Corner._createRoundFragment(r, f, b, true );           
            ds.appendChild(ls);
            nh += r;
        }
       
         if (h) {
            Element.setStyle( t, { height: nh + 'px' } );     
        }       
       
        t.appendChild(ds);  
    } ,
   
    _createRoundFragment: function (r, f, c, b) {
         var ls = document.createDocumentFragment();
         var l = null ;
         var m = ml = mr = null ;
         var j = 0 ;
         for (i = 1 ; i <= r; i ++ ) {
            l = document.createElement('div');
           
             // ����margin
            j = b ? i : r - i + 1 ;
            m = Math.sqrt(r * r - j * j);           
            m = Math.round(r - m) + 'px';
           
             if (b) {
                ml = f & Corner.BOTTOM_LEFT ? m : '0px';
                mr = f & Corner.BOTTOM_RIGHT ? m : '0px';           
            } else {
                ml = f & Corner.TOP_LEFT ? m : '0px';
                mr = f & Corner.TOP_RIGHT ? m : '0px';           
            }
             Element.setStyle( l, { backgroundColor: c,
                                   fontSize: '1px',
                                   height: '1px',                                  
                                   marginLeft: ml,
                                   marginRight: mr,
                                   overflowX: 'hidden',
                                   overflowY: 'hidden' } );
            ls.appendChild(l);
        }
         return ls;
    }
}