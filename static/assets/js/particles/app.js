particlesJS('particles-js',{
  particles:{
    number:{ value:60,       /* weniger Partikel = ruhiger */
             density:{ enable:true, value_area:800 }},
    color:{ value:'#ffffff' },
    shape:{ type:'circle' },
    opacity:{ value:0.6 },   /* dezenter */
    size:{ value:3, random:true },
    line_linked:{
      enable:true,
      distance:120,
      color:'#ffffff',
      opacity:0.2,          /* feiner Linien-Schleier */
      width:1
    },
    move:{
      enable:true,
      speed:1.2,            /* langsamer = eleganter */
      out_mode:'out'
    }
  },
  interactivity:{           /* >>> alles abschalten <<< */
    detect_on:'canvas',
    events:{
      onhover:{ enable:false },
      onclick:{ enable:false },
      resize:false          /* spart etwas Rechenzeit */
    }
  },
  retina_detect:true
});
