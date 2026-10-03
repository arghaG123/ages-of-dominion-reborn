// Authored design coordinates only. No game state, pathfinding or simulation.
// Cell origins use [column,row]; actor and approach anchors use cell centres.
const MAP_SPACE = {
  adventure: {
    title:'Adventure · town, crossing and discoveries', cols:16, rows:10,
    camera:{yaw:15,elevation:55,unit:80},
    reference:'../docs/plan/references/owner-additions-2026-10-02/image_4f5e15d7.jpg',
    comparison:'Town in the upper middle; gate road descends to the hero junction. A stone crossing leads west to a mill and shrine. The forest dwelling sits southeast; a guarded ruin sits northeast. These relationships follow the reference; the coordinates are a new proposal.',
    river:[[4,0],[5,0],[4,1],[5,1],[4,2],[5,2],[4,3],[5,3],[4,4],[5,4],[4,5],[5,5],[4,6],[5,6],[4,7],[5,7],[4,8],[5,8],[4,9],[5,9]],
    banks:[[4.3,0],[4.1,2],[4.35,4],[4.05,6],[4.2,8],[4.35,10],[5.75,10],[5.9,8],[5.95,6],[5.7,4],[5.9,2],[5.7,0]],
    obstacles:[[0,4],[0,5],[0,6],[0,7],[0,8],[0,9],[1,7],[14,8],[15,8],[14,9],[15,9],[14,0],[15,0],[15,1],[15,2],[15,3],[15,4],[15,5]],
    bridges:[{id:'B1',label:'Stone crossing',rect:[3.75,6.05,2.5,.9],cells:[[4,6],[5,6]],approaches:[[3,6],[6,6]]}],
    sites:[
      {id:'A1',label:'Fortified town',rect:[7,1,3,3],approach:[8,4],facing:'South gate / +row',kind:'settlement'},
      {id:'A2',label:'Guarded ruin',rect:[12,1,2,2],approach:[12,3],facing:'South opening / +row',kind:'ruin'},
      {id:'A3',label:'Mill clearing',rect:[1,4,2,2],approach:[2,6],facing:'South approach / +row',kind:'site'},
      {id:'A4',label:'Mine apron',rect:[11,6,2,2],approach:[10,6],facing:'West entrance / −column',kind:'mine'},
      {id:'A5',label:'Forest dwelling',rect:[11,8,2,2],approach:[10,8],facing:'West opening / −column',kind:'dwelling'},
      {id:'A6',label:'Shrine clearing',rect:[1,8,2,2],approach:[2,7],facing:'North opening / −row',kind:'site'}
    ],
    resources:[{id:'F',label:'Food',cell:[3,8]},{id:'W',label:'Wood',cell:[7,9]},{id:'S',label:'Stone',cell:[14,5]},{id:'G',label:'Gold',cell:[10,4]}],
    guards:[{id:'G1',label:'Ruin guard',cell:[12,4]},{id:'G2',label:'Mine guard',cell:[10,5]}],
    actors:[{id:'H',label:'Hero start',cell:[8,8],team:'allied'}],
    roads:[
      {id:'town',cells:[[8,4],[8,5],[8,6],[8,7],[8,8]]},
      {id:'crossing',cells:[[8,8],[8,7],[7,7],[7,6],[6,6],[5,6],[4,6],[3,6],[2,6]]},
      {id:'mill',cells:[[2,6],[2,7]]},
      {id:'ruin',cells:[[8,6],[9,6],[9,5],[9,4],[10,4],[11,4],[12,4],[12,3]]},
      {id:'mine',cells:[[8,6],[9,6],[10,6]]},
      {id:'mineGuard',cells:[[10,6],[10,5]]},
      {id:'dwelling',cells:[[8,8],[9,8],[10,8]]},
      {id:'food',cells:[[2,7],[3,7],[3,8]]},
      {id:'wood',cells:[[8,8],[8,9],[7,9]]},
      {id:'stone',cells:[[11,4],[11,5],[12,5],[13,5],[14,5]]}
    ],
    route:[[8,8],[8,7],[7,7],[7,6],[6,6],[5,6],[4,6],[3,6],[2,6],[2,7]],
    selected:'H',focus:[3,4,7,5.5],
    labels:[{text:'North ridge',at:[11,0]},{text:'Wood',at:[.5,6]},{text:'Forest',at:[14,8.5]}]
  },
  tactical:{
    title:'Tactical · two banks, two crossing lanes',cols:7,rows:10,
    camera:{yaw:15,elevation:40,unit:96},
    reference:'../docs/plan/references/owner-additions-2026-10-02/image_27abdc40.jpg',
    comparison:'The mock stages allied groups near the left foreground and enemies deeper across a stream. This proposal keeps that separation and reserves two stone decks with open approaches. The reference’s hex markings and pictured factions are not adopted.',
    river:Array.from({length:10},(_,r)=>[3,r]),
    banks:[[3.15,0],[3.3,2],[3.1,3],[3.18,5],[3.08,7],[3.28,9],[3.2,10],[3.85,10],[3.75,9],[3.92,7],[3.8,5],[3.9,3],[3.78,2],[3.9,0]],
    obstacles:[[0,0],[1,0],[0,1],[6,0],[6,1],[0,5],[6,5],[6,8],[6,9],[5,9]],
    bridges:[{id:'B1',label:'Upper deck',rect:[2.75,3.1,1.5,.8],cells:[[3,3]],approaches:[[2,3],[4,3]]},{id:'B2',label:'Lower deck',rect:[2.75,7.1,1.5,.8],cells:[[3,7]],approaches:[[2,7],[4,7]]}],
    sites:[],resources:[],guards:[],
    actors:[
      {id:'C',label:'Commander (0,9)',cell:[0,9],team:'allied',commander:true},
      {id:'L1',label:'Melee slot',cell:[1,8],team:'allied'},
      {id:'L2',label:'Ranged slot',cell:[1,4],team:'allied'},
      {id:'L3',label:'Heavy slot',cell:[2,1],team:'allied'},
      {id:'R1',label:'Enemy slot 1',cell:[5,2],team:'enemy'},
      {id:'R2',label:'Enemy slot 2',cell:[5,4],team:'enemy'},
      {id:'R3',label:'Enemy slot 3',cell:[5,7],team:'enemy'}
    ],
    roads:[{id:'upperLane',cells:[[1,3],[2,3],[3,3],[4,3],[5,3]]},{id:'lowerLane',cells:[[1,8],[1,7],[2,7],[3,7],[4,7]]}],
    deployment:[{team:'allied',rect:[0,6,3,4]},{team:'enemy',rect:[4,0,3,4]}],
    route:[[1,8],[1,7],[2,7],[3,7],[4,7]],selected:'L1',focus:[0,6,5.8,3.5],
    labels:[{text:'Distant ruins',at:[3,0]},{text:'Rock',at:[6,9.6]}]
  }
};
