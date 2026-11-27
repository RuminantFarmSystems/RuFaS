/* Decimal inputs: accept comma or point, never thousands separators. */
(function(root){
  function parseDecimal(raw,label,optional=false){
    const text=String(raw??'').trim();
    if(text===''){if(optional)return null;throw Error(label+': informe um valor.');}
    if(!/^[+]?(?:\d+(?:[.,]\d+)?|[.,]\d+)$/.test(text))throw Error(label+': use ponto ou vírgula decimal, sem separador de milhar.');
    const value=Number(text.replace(',','.'));
    if(!Number.isFinite(value)||value<0)throw Error(label+': informe um número não negativo.');
    return value;
  }
  root.parseDecimal=parseDecimal;
  if(typeof module!=='undefined')module.exports={parseDecimal};
})(globalThis);
