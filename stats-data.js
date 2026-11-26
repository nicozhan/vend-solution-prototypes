/* ==========================================================================
   VendSolution · 统计模块共享数据（stats.html / stats-fleet.html / stats-rank.html 共用）
   与 App 其它页面保持一致：
   - 点位 8 个，设备数取自 site-list.html（12/3/6/4/2/3/5/3 = 38 台）
   - 设备 SN 生成规则与 site-detail.html 相同（类型前缀-序号）
   - 商品目录 50 个，其中 15 个与 product-list.html 的补货清单同名
   所有金额均为「区间销售额」，随 M44 时间筛选缩放；名次按销售额降序。
   ========================================================================== */
window.STATS=(function(){
  var PERIODS={
    today:{key:'today',label:'今日',days:1,range:'11-26',total:12860,orders:286,prevTotal:11940,prevOrders:271,prevLabel:'昨日同期'},
    d7:{key:'d7',label:'近 7 天',days:7,range:'11-20 至 11-26',total:128400,orders:2860,prevTotal:118700,prevOrders:2774,prevLabel:'前 7 天'},
    d30:{key:'d30',label:'近 30 天',days:30,range:'10-28 至 11-26',total:528600,orders:11820,prevTotal:501300,prevOrders:11240,prevLabel:'前 30 天'}
  };
  var ORDER=['today','d7','d30'];
  var SEED={today:1.37,d7:0,d30:2.61};

  /* 点位：share 为区间销售额占比（合计 100） */
  var SITES=[
    {id:'s1',name:'曼谷机场 T1 店',devices:12,status:'ACTIVE',share:26},
    {id:'s2',name:'中央广场咖啡角',devices:3,status:'ACTIVE',share:8},
    {id:'s3',name:'素坤逸 24 便利店',devices:6,status:'ACTIVE',share:19},
    {id:'s4',name:'拉玛九商场店',devices:4,status:'PAUSED',share:9},
    {id:'s5',name:'是隆路写字楼店',devices:2,status:'ACTIVE',share:6},
    {id:'s6',name:'湄南河码头店',devices:3,status:'ACTIVE',share:11},
    {id:'s7',name:'邦纳工业园店',devices:5,status:'ACTIVE',share:20},
    {id:'s8',name:'拉抛 Central 店',devices:3,status:'CLOSED',share:1}
  ];
  var TYPES=[['GRAB_GO','开门柜'],['VENDING','弹簧机'],['COFFEE','现调机'],['DRINK','饮料机']];

  /* 商品目录：前 5 名的金额与文档 M17/M21 的示例一致（¥9,860 / 8,420 / 7,940 / 6,120 / 5,280） */
  var CATALOG=[
    ['气泡水 青柠 500ml','饮料'],['薯片 原味 70g','零食'],['能量饮料 250ml','饮料'],
    ['巧克力 50g','零食'],['矿泉水 600ml','饮料'],['椰子水 330ml','饮料'],
    ['泰式奶茶 330ml','饮料'],['鲜榨橙汁 250ml','饮料'],['柠檬茶 480ml','饮料'],
    ['烤海苔 40g','零食'],['原味酸奶 180g','乳制品'],['三文鱼饭团 110g','即食'],
    ['冰红茶 500ml','饮料'],['混合坚果 30g','零食'],['巧克力棒 45g','零食'],
    ['草莓酸奶 180g','乳制品'],['火腿三明治 150g','即食'],['乌龙茶 500ml','饮料'],
    ['可乐 330ml','饮料'],['雪碧 330ml','饮料'],['薯片 番茄 70g','零食'],
    ['鸡蛋布丁 120g','乳制品'],['巧克力牛奶 200ml','乳制品'],['鲜牛奶 250ml','乳制品'],
    ['维他命水 500ml','饮料'],['美式咖啡 270ml','饮料'],['咖啡拿铁 270ml','饮料'],
    ['豆浆 300ml','饮料'],['芒果果汁 300ml','饮料'],['苏打水 原味 500ml','饮料'],
    ['酸梅汤 350ml','饮料'],['饼干 黄油 100g','零食'],['威化 巧克力 60g','零食'],
    ['果冻 综合 120g','零食'],['牛肉干 50g','零食'],['爆米花 焦糖 80g','零食'],
    ['米饼 原味 60g','零食'],['软糖 葡萄 50g','零食'],['坚果棒 40g','零食'],
    ['奶酪棒 25g','乳制品'],['芝士条 30g','乳制品'],['乳酸菌饮品 100ml','乳制品'],
    ['奶油蛋糕 90g','乳制品'],['豆奶 250ml','乳制品'],['鸡肉卷 140g','即食'],
    ['关东煮 组合 180g','即食'],['卤蛋 2 枚','即食'],['杯面 65g','即食'],
    ['沙拉 鸡胸 200g','即食'],['火腿三明治 双拼 170g','即食']
  ];
  var TOP5=[9860,8420,7940,6120,5280];

  function period(key){return PERIODS[key]||PERIODS.d7}
  function money(n){return '¥'+Math.round(n).toLocaleString('en-US')}
  function num(n){return Math.round(n).toLocaleString('en-US')}
  function pctText(x,digits){var d=digits==null?1:digits;return (x>=0?'+':'−')+Math.abs(x).toFixed(d)+'%'}
  function delta(cur,prev){return prev?((cur-prev)/prev*100):0}

  /* ---------- 设备 ---------- */
  function buildDevices(){
    var out=[];
    SITES.forEach(function(site,si){
      var amount=site.share/100;
      var weights=[];
      for(var i=0;i<site.devices;i++)weights.push(1+0.35*Math.sin((i+1)*1.9+si));
      var sum=weights.reduce(function(a,b){return a+b},0);
      for(var i=0;i<site.devices;i++){
        var t=TYPES[i%4];
        var active=!(site.status==='CLOSED')&&!(site.id==='s4'&&i>=2)&&!(site.id==='s2'&&i===2);
        out.push({
          sn:t[0].slice(0,4)+'-'+(10000+si*1000+site.devices*100+i*37+11),
          type:t[0],typeLabel:t[1],
          siteId:site.id,site:site.name,
          active:active,
          weight:amount*weights[i]/sum
        });
      }
    });
    return out;
  }
  var DEVICES=buildDevices();

  /* ---------- 商品权重 ---------- */
  function productWeights(){
    /* TOP5 用文档给的金额换算成百分比；其余 45 个按递减权重归一到剩余 70.7% */
    var base=TOP5.map(function(v){return v/1284});
    var used=base.reduce(function(a,b){return a+b},0);
    var tailTotal=100-used;
    var raw=0,scaled=[];
    for(var i=5;i<CATALOG.length;i++){
      var jitter=0.90+0.20*Math.abs(Math.sin(i*12.9898));
      var v=Math.pow(0.97,i-5)*jitter;
      scaled.push(v); raw+=v;
    }
    return base.concat(scaled.map(function(v){return v/raw*tailTotal}));
  }
  var WEIGHTS=productWeights();

  var RANK_CACHE={};
  function ranks(key){
    if(RANK_CACHE[key])return RANK_CACHE[key];
    var per=period(key),total=per.total,seed=SEED[key]||0;
    var ws=WEIGHTS.map(function(w,i){return seed?w*(1+0.28*Math.sin((i+1)*1.7+seed)):w});
    var sum=ws.reduce(function(a,b){return a+b},0);

    var prods=CATALOG.map(function(c,i){
      return {name:c[0],sub:c[1],amount:total*ws[i]/sum,share:ws[i]/sum*100};
    }).sort(function(a,b){return b.amount-a.amount});

    var siteSum=SITES.reduce(function(a,s){return a+s.share},0);
    var sites=SITES.map(function(s){
      return {name:s.name,sub:s.devices+' 台设备 · '+(s.status==='ACTIVE'?'运营中':s.status==='PAUSED'?'已暂停':'已关闭'),amount:total*s.share/siteSum,share:s.share/siteSum*100};
    }).sort(function(a,b){return b.amount-a.amount});

    var devs=DEVICES.map(function(d){
      return {name:d.sn,sub:d.site+' · '+d.typeLabel,amount:total*d.weight,share:d.weight*100,inUse:d.active};
    }).sort(function(a,b){return b.amount-a.amount});

    RANK_CACHE[key]={products:prods,sites:sites,devices:devs};
    return RANK_CACHE[key];
  }

  /* ---------- 资产 ---------- */
  function assets(){
    var active=DEVICES.filter(function(d){return d.active}).length;
    var models=TYPES.map(function(t){
      return {name:t[1],count:DEVICES.filter(function(d){return d.type===t[0]}).length};
    }).sort(function(a,b){return b.count-a.count});
    return {
      deviceTotal:DEVICES.length,
      deviceActive:active,
      deviceRate:active/DEVICES.length*100,
      siteTotal:SITES.length,
      siteActive:SITES.filter(function(s){return s.status==='ACTIVE'}).length,
      sitePaused:SITES.filter(function(s){return s.status==='PAUSED'}).length,
      siteClosed:SITES.filter(function(s){return s.status==='CLOSED'}).length,
      productTotal:15,
      productOnShelf:13,
      productLowStock:4,
      productRate:13/15*100,
      models:models
    };
  }

  /* ---------- 现场待办（G5） ---------- */
  var TODO={
    lowStockProducts:6,
    planDevices:12,
    checkedDevices:7,
    diffIn:12,
    diffOut:-5,
    diffTop:[
      {name:'气泡水 青柠 500ml',diff:8},
      {name:'薯片 原味 70g',diff:-4},
      {name:'泰式奶茶 330ml',diff:3}
    ]
  };

  var TODAY={amount:12860,orders:286};

  return {
    PERIODS:PERIODS,ORDER:ORDER,SITES:SITES,TYPES:TYPES,TODO:TODO,TODAY:TODAY,
    period:period,ranks:ranks,assets:assets,devices:function(){return DEVICES},
    money:money,num:num,pctText:pctText,delta:delta
  };
})();
