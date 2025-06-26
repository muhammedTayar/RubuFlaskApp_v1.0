(function () {
  if (window.crypto && typeof window.crypto.randomUUID === 'function') return;
  const lut = [...Array(256)].map((_,i)=>(i+0x100).toString(16).substr(1));
  if (!window.crypto) window.crypto = {};
  window.crypto.randomUUID = () => {
    const d = crypto.getRandomValues(new Uint8Array(16));
    d[6] = d[6] & 0x0f | 0x40;            // Version 4
    d[8] = d[8] & 0x3f | 0x80;            // Variant 10
    return  lut[d[0]]+lut[d[1]]+lut[d[2]]+lut[d[3]]+'-'+
            lut[d[4]]+lut[d[5]]+'-'+lut[d[6]]+lut[d[7]]+'-'+
            lut[d[8]]+lut[d[9]]+'-'+
            lut[d[10]]+lut[d[11]]+lut[d[12]]+lut[d[13]]+lut[d[14]]+lut[d[15]];
  };
})();