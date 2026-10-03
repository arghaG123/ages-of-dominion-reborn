export function project(matrix, [x, y]) { const [a,b,c,d,e,f] = matrix; return [a*x+c*y+e,b*x+d*y+f]; }
export function inverse(matrix, [x, y]) {
  const [a,b,c,d,e,f] = matrix, det = a*d-b*c;
  if (Math.abs(det) < 1e-8) throw new Error('Noninvertible camera');
  return [(d*(x-e)-c*(y-f))/det,(-b*(x-e)+a*(y-f))/det];
}
export function camera(source, width, height) {
  const scale = Math.min(width/source[0], height/source[1]);
  return { scale, offset: [(width-source[0]*scale)/2,(height-source[1]*scale)/2] };
}
