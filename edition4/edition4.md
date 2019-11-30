# 第四期-使用Appium测试手机Web App

Appium刚开始的时候是用来测试原生App的，直到现在这也还是Appium的核心价值主张。当然了Appium不仅仅只支持测试原生App， 同时还支持测试其他类型的app。基本上有如下三类：
1. 原生App(Native apps). 原生App指的是那些用原生Api和操作系统提供的SDK便携构建的程序。用户可以通过官方的应用商店获取到这类App，然后通过点击设备屏幕上的应用图标来运行App。
2. Web App. 这些App是通过HTML/JS/CSS编写，然后部署在web服务器上。用户通过手机浏览器上输入相应的URL进行访问这类App。
3. 混合APP. 这类app是融合了上面两种模式。混合App就像套着一层原生APP的外壳，它可能有大量的原生UI，也可能完全没有原生的UI。在一些界面上会内嵌一些UI组件，这类组件被称作为“web view”，它的本质就是一个chromeless类型的web浏览器。这些webview可以访问本地或者远程资源。一些混合型App所有的功能特性都是使用HTML/JS/CSS完成的，然后和原生app打包，然后通过webview来实现功能操作。当然不管混合App是怎么产生的，他们只有两种模式分别是原生和Web。Appium都是可以进行操作饿的。(更多的关于混合型App将在后续的专栏中讲到)。

我们可以通过设置不同的能力集(desired capabilities)来让Appium在安卓和苹果设备上对各种类型的app进行自动化操作。我们会发现在测试基于Appium的移动web测试其实就和执行Selenium测试是一致的，这是因为两者都遵循了WebDriver协议。实际上，我们都可以使用标准的Selenium客户端来和Appium的服务端做交互从而达到测试手机web应用，达到这样的效果只需要我们在能力集中用```browserName```这个属性来替换```app```这个属性就好了，然后Appium就会启动对应的浏览器，加载一些执行环境上下文，从而达到你可以使用常规的Selenium方法（类似于通过CSS查找元素，前往不同的URL地址）。

在做手机应用的自动化测试的时候，我们写的代码在不同平台上都是适用的。就像我们写Selenium的脚本时，不需要关注我们是用Firefox还是Chrome。同理我们Appium的web测试代码同样也不需要关注我们是在苹果手机上使用Safari还是在安卓上使用Chrome。那接下来我们就看一下使用这两种不同的手机浏览器时我们需要怎么设置我们的能力集：
```java
// 在苹果上使用Safari
DesiredCapabilities capabilities = new DesiredCapabilities();
capabilities.setCapability("platformName", "iOS");
capabilities.setCapability("platformVersion", "11.2");
capabilities.setCapability("deviceName", "iPhone 7");
capabilities.setCapability("browserName", "Safari");

// 在安卓上使用Chrome
DesiredCapabilities capabilities = new DesiredCapabilities();
capabilities.setCapability("platformName", "Android");
capabilities.setCapability("deviceName", "Android Emulator");
capabilities.setCapability("browserName", "Chrome");
```
当我们启动了正确的`RemoteWebDriver`会话，我们就可以做我们想做的一些操作。举一个例子，比如我们想前往当前这个界面。
```java
driver.get("https://appiumpro.com");
String title = driver.getTitle();
// 这里我们可能需要验证一下我们的标题是否包含Appium Pro
```

## 使用苹果真机时的注意事项
Appium要与Safari进行交互（通过浏览器公开的远程调试器）是有一个前置步骤，那便是需要先将 `WebKit remote debug protocol`翻译成`Apple's iOS web inspector protocol`.是不是听起来很复杂。不过幸好的是Google伟大的工程师为我们提供了一个可以进行这项翻译工作的工具，我们称它为[ios-webkit-debug-proxy](https://github.com/google/ios-webkit-debug-proxy)(IWDP).在真机上运行Safari或者是混合型App测试时，我们一定要实现安装好IWDP。关于更多为什么我们需要这样做，我们可以参考[Appium IWDP doc](https://appium.io/docs/en/writing-running-appium/web/ios-webkit-debug-proxy/).那我们如果装好了IWDP，这个时候我们只需要在能力集中简单的添加两个属性`udid`,`startIWDP`.
```java
// 在真机上使用Safari需要的格外参数
capabilities.setCapability("udid", "<the id of your device>");
capabilities.setCapability("startIWDP", true);
```
如果你的能力集中没有添加`startIWDP`这个属性，那么你就必须自己运行IWDP，然后Appium会假定它在监听这所有的请求。

*标注：在苹果真机运行测试自身就是一个比较大的话题，这个话题会在后续的Appium Pro的专题中再细讲。当然你也可以在Appium的文档中查看[真机测试文档](https://appium.io/docs/en/drivers/ios-xcuitest-real-devices/)*

## 使用安卓的注意事项
幸运的是，不管使用安卓虚拟机还是安卓真机，Appium都可以利用[Chromedriver](https://sites.google.com/a/chromium.org/chromedriver/)来完成相应的工作。当我们想要自动化测试任何基于Chrome的浏览器或者是webview时，我们无需做任何事情，Appium会在底层帮我们创建管理一个新的Chromedriver进程，从而我们可以直接使用WebDriver提供的所有功能。当然我们可能需要关注的一点是我们安卓设备上的Chrome是不是和Appium使用的Chromedriver是够兼容。如果不兼容的话，我们会看到这样一个错误消息提示我们需要更新Chrome。
如果你不想更新Chrome，那我们可以在安装Appium的时候通过`--chromedriver_version`选项来明确指出我们要安装的Chromedriver版本。举例如下：
`npm install -g appium --chromedriver_version="2.35"`

我们怎么直到需要安装什么版本的Chromedriver？Appium团队给我们维护了一个很有用的文档，关于什么版本的Chromedriver支持什么版本的Chrome，文档地址在[Chromedriver指导书](https://appium.io/docs/en/writing-running-appium/web/chromedriver/)

## 完整的示例程序
下面我们要通过一个场景来验证同一份代码是可以同时适用于苹果设备和安州设备的。场景是测试AppiumPro的联系我们的这样一个功能。我们验证的点是如果一个人不填写验证码进行登陆，会有一个正确的错误提出给出。下面是我们关系的测试逻辑代码：
```java
driver.get("http://appiumpro.com/contact");
wait.until(ExpectedConditions.visibilityOfElementLocated(EMAIL))
.sendKeys("foo@foo.com");
driver.findElement(MESSAGE).sendKeys("Hello!");
driver.findElement(SEND).click();
String response = wait.until(ExpectedConditions.visibilityOfElementLocated(ERROR)).getText();

// validate that we get an error message involving a captcha, which we didn't fill out
Assert.assertThat(response, CoreMatchers.containsString("Captcha"));
```
可以看到为了可读性我在类中设置了一些变量，然后我们需要一些样板代码来给我们的IOS和安卓设置能力集。测试代码如下：
```java
mport io.appium.java_client.AppiumDriver;
import io.appium.java_client.android.AndroidDriver;
import io.appium.java_client.ios.IOSDriver;
import java.net.MalformedURLException;
import java.net.URL;
import org.hamcrest.CoreMatchers;
import org.junit.Assert;
import org.junit.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.remote.DesiredCapabilities;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

public class Edition004_Web_Testing {

private static By EMAIL = By.id("contactEmail");
private static By MESSAGE = By.id("contactText");
private static By SEND = By.cssSelector("input[type=submit]");
private static By ERROR = By.cssSelector(".contactResponse");

@Test
public void testAppiumProSite_iOS() throws MalformedURLException {
DesiredCapabilities capabilities = new DesiredCapabilities();
capabilities.setCapability("platformName", "iOS");
capabilities.setCapability("platformVersion", "11.2");
capabilities.setCapability("deviceName", "iPhone 7");
capabilities.setCapability("browserName", "Safari");

// Open up Safari
IOSDriver driver = new IOSDriver<>(new URL("http://localhost:4723/wd/hub"), capabilities);
actualTest(driver);
}

@Test
public void testAppiumProSite_Android() throws MalformedURLException {
DesiredCapabilities capabilities = new DesiredCapabilities();
capabilities.setCapability("platformName", "Android");
capabilities.setCapability("deviceName", "Android Emulator");
capabilities.setCapability("browserName", "Chrome");

// Open up Safari
AndroidDriver driver = new AndroidDriver(new URL("http://localhost:4723/wd/hub"), capabilities);
actualTest(driver);
}

public void actualTest(AppiumDriver driver) {
// Set up default wait
WebDriverWait wait = new WebDriverWait(driver, 10);

try {
driver.get("http://appiumpro.com/contact");
wait.until(ExpectedConditions.visibilityOfElementLocated(EMAIL))
.sendKeys("foo@foo.com");
driver.findElement(MESSAGE).sendKeys("Hello!");
driver.findElement(SEND).click();
String response = wait.until(ExpectedConditions.visibilityOfElementLocated(ERROR)).getText();

// validate that we get an error message involving a captcha, which we didn't fill out
Assert.assertThat(response, CoreMatchers.containsString("Captcha"));
} finally {
driver.quit();
}

}
}
```

这就是我们开始使用Appium测试web需要掌握的知识。同样你可以在[这](https://github.com/cloudgrey-io/appiumpro/blob/master/java/src/test/java/Edition004_Web_Testing.java)找到我们的源代码。