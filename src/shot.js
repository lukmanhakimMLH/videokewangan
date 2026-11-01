const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:+process.argv[4]||900,height:+process.argv[5]||1200}});
await p.goto('file://'+require('path').resolve(process.argv[2]));await p.waitForTimeout(800);await p.screenshot({path:process.argv[3],fullPage:true});await b.close();})();
