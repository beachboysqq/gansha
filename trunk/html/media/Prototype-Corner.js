var Corner = {
     // 标志圆角位置的旗标
    TOP_LEFT:     0x1 ,
    TOP_RIGHT:     0x2 ,
    BOTTOM_LEFT:   0x4 ,
    BOTTOM_RIGHT: 0x8 ,
    ALL:           0xf ,
   
     /**/ /* *******************************************************
    * target: 要圆角的目标元素
    * radius: 圆角的半径，默认值为5
    * flags: 圆角位置的旗标或其组合，默认值为全部
    * backgroundColor: 圆角的背景色，默认值为目标元素的背景色
    ******************************************************* */
     round: function (target, radius, flags, backgroundColor) {
         var t = $(target);
         var r = radius || 5 ;
         var f = flags || Corner.ALL;
         var c = Element.getStyle(t, 'backgroundColor');
         var b = backgroundColor || c;
       
         // 修正在IE里元素样式为FLOAT时，圆角DIV宽度为0的BUG
         var ft = Element.getStyle(t, ' float ');
         if (navigator.appVersion.match( / \bMSIE\b / ) && ft != 'none' && ! t.style.width) {           
            Element.setStyle(t, { width: Element.getWidth(t) + 'px' } );
        }
       
         // 创建DIV，并把目标元素的内容剪切到其中
         var d = document.createElement('div');         
        d.innerHTML = t.innerHTML;
        t.innerHTML = '';       
       
         // 设置新DIV的背景色为目标元素的背景色，并目标元素为透明背景
         Element.setStyle( d, { backgroundColor: c } );     
        Element.setStyle( t, { backgroundColor: 'transparent' } );     
       
         // 设置新DIV的高度为目标元素的高度
         var h = t.style.height;
         var nh = 0 ;
         if (h) {
            Element.setStyle( d, { height: h } );
            nh = parseInt(h);
        }                   
       
         // 设置新DIV的缩进
         var p = Element.getStyle(t, 'padding');
         if (p) {
            Element.setStyle( d, { padding: p } );           
            Element.setStyle( t, { padding: '0px 0px 0px 0px' } );
        }         
       
         // 创建用于新DIV和圆角DIV的文档片段，这样避免每次设置元素样式或添加新元素时重绘页面，提高效率
         var ds = document.createDocumentFragment();               
         var ls = null ;
         // 创建顶部圆角DIV
          if (f & (Corner.TOP_LEFT | Corner.TOP_RIGHT)) {
            ls = Corner._createRoundFragment(r, f, b , false );           
            ds.appendChild(ls);            
            nh += r;
        }       
       
        ds.appendChild(d);
       
         // 创建底部圆角DIV
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
           
             // 计算margin
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