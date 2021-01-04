const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({
    headless: false,
    // devtools: true,
    defaultViewport: {
      width: 1920,
      height: 1080,
    }
  })
  const page = await browser.newPage()
  await page.goto("http://192.168.1.200:9001/user/login")
  // //登录按钮出现后点击
  // await page.waitForSelector(".login_register")
  // await page.click("a[href='/user/login']")
  //出现登录窗口后输入信息并点击验证按钮
  await page.waitForSelector("input[name=user]")
  await page.type("input[name=user]", "18833332222", { delay: 10 })
  await page.type('input[type=password]', '000000000', {delay: 10})
  await page.waitForSelector('.login_btn')
  await page.click('.login_btn')
  await slider()
  await page.waitFor(800)
  await page.waitForSelector('.submit')
  await page.click('.submit')
  await page.waitFor(5000)

  async function slider() {
    //等待canvas完成 并完成0.5s的移动动画 (验证出错也可为等待时间)
    await page.waitForSelector('.geetest_ready')
    await page.waitFor(500)
    //获取canvas的左上角X坐标作为滑动的基坐标
    await page.waitForSelector('.geetest_canvas_bg')
    let canvasCoordinate = await page.$(".geetest_canvas_bg");
    let canvasBox = await canvasCoordinate.boundingBox();
    let canvasX = canvasBox.x;
    //等待滑动按钮出现获取Y坐标
    await page.waitForSelector('.geetest_slider_button')
    let button = await page.$(".geetest_slider_button");
    let box = await button.boundingBox();
    let mouseY = Math.floor(box.y + box.height / 2);
    //计算位移
    let moveDistance = await compare()
    //滑动验证
    await page.hover('.geetest_slider_button')
    await page.mouse.down()
    await page.mouse.move(canvasX + moveDistance / 3, mouseY, { steps: 15 })
    await page.waitFor(1 * 30)
    await page.mouse.move(canvasX + moveDistance / 2, mouseY, { steps: 20 })
    await page.waitFor(2 * 50)
    await page.mouse.move(canvasX + moveDistance + 10, mouseY, { steps: 18 })
    await page.waitFor(3 * 80)
    await page.mouse.move(canvasX + moveDistance / 1, mouseY, { steps: 60 })
    await page.waitFor(4 * 30)
    await page.mouse.up()
    await page.waitForSelector('.geetest_success_radar_tip_content')
    //是否验证成功
    let state = await page.evaluate(() => {
      return document.querySelector('.geetest_success_radar_tip_content').innerText;
    })
    if (state !== '验证成功') {
      return slider();
    }
  }

  //计算位移
  async function compare() {
    // 获取canvas
    let moveDistance = await page.evaluate(() => {
      let fullbgs = document.querySelector('.geetest_canvas_fullbg');
      let bgs = document.querySelector('.geetest_canvas_bg');
      let bgsCtx = bgs.getContext('2d');
      let fullbgsCtx = fullbgs.getContext('2d');
      let canvasWidth = bgsCtx.canvas.width;
      let canvasHeight = bgsCtx.canvas.height;
      //最大像素差(阀值)
      // let pixelsDifference = 100;
      let pixelsDifference = 70;
      //第一个超过阀值的x坐标 最后一个超过阀值的x坐标
      let firstX, lastX;
      //对比像素
      for (let i = 1, k = 1; i < canvasWidth; i++) {
        if (!firstX) {
          //找到第一个超过阀值的X坐标后 Y轴停止循环
          for (let j = 1; j < canvasHeight; j++) {
            //获取像素数据
            let bgsPx = bgsCtx.getImageData(i, j, 1, 1).data;
            let fullbgsPx = fullbgsCtx.getImageData(i, j, 1, 1).data;
            //计算像素差 并判断是否超过阀值
            let res1 = Math.abs(bgsPx[0] - fullbgsPx[0])
            let res2 = Math.abs(bgsPx[1] - fullbgsPx[1])
            let res3 = Math.abs(bgsPx[2] - fullbgsPx[2])
            if (res1 > pixelsDifference || res2 > pixelsDifference || res3 > pixelsDifference) {
              firstX = i;
              //记录Y坐标
              k = j;
            }
          }
        } else {
          //顺着X轴查找最后一个超过阀值的X坐标
          //K是第一个超过阀值的Y坐标
          //(会多一点循环时间 但是不用手动测量阴影块宽度)
          let bgsPx = bgsCtx.getImageData(i, k, 1, 1).data;
          let fullbgsPx = fullbgsCtx.getImageData(i, k, 1, 1).data;
          let res1 = Math.abs(bgsPx[0] - fullbgsPx[0])
          let res2 = Math.abs(bgsPx[1] - fullbgsPx[1])
          let res3 = Math.abs(bgsPx[2] - fullbgsPx[2])
          if (res1 > pixelsDifference || res2 > pixelsDifference || res3 > pixelsDifference) {
            lastX = i;
          }
        }
      }
      //滑动到阴影块中心的距离
      return firstX + (lastX - firstX) / 2;
    })
    return moveDistance;
  }

  // await browser.close()
})();