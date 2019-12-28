# 使用Deep Link使测试加速
在我们做功能测试的时候我们会遇到一个问题，就是测试速度太慢了。不同的测试框架的速度都是不一致的，这里首先要承认Appium的速度并没有总是达到我预期的速度。速度本事又是另外一个话题了。这一篇专栏主要是通过一些“快捷方式”使我们的测试提速。

那什么是我说的"快捷方式"呢？我们拿登录做例子。绝大多数的App都会有登录的步骤，在进行测试其他功能使，我们必须要先执行登录操作。如果我们将我们的测试用例保持原子性，我们也应该这样做，每一个测试用例都将需要单独的执行登录操作。这将会造成很大的时间上的浪费。因为我们其实应该只在我们测试登录逻辑的时候，去执行一些Appium的命令，当我们测试其他测试用例的时候，最好是可以直接跳过认证直接进行业务逻辑验证。

在IOS和Android上，我们可以通过一个叫做deep link的来实现。Deep Link是一种特殊的URls，它可以与特定的apps进行关联。app的开发者需要在OS上注册一个唯一的URL方案。这样之后app就可以启动并且根据URL里的内容进行想要的操作。

那我们需要的就是一个特定的URL能让我们的APP进行登录尝试。当我们检测到了一个URL被激活的时候，app将在后台进行登录操作然后重定向到登录后的页面。

最近，我花了一点时间给[The App](https://github.com/cloudgrey-io/the-app)增加了deep link。至于我是怎么完成deep link添加的就已经超过了本文所讨论的范围了。网络上有很多的指导教程关于怎么给iOs和androidapp增加deep link的。我发布了the app v1.2.1版本，这个版本支持了deep link，url类似于这样：
```java
theapp://login/<username>/<password>
```

换一句话说，就是只要我们在设备上安装了The App， 那么哦们就可以通过上述形势的Url达到启动app，根据Url提供的username和password进行登录验证，然后跳转到登录后的页面。现在让我们看一下怎么通过Appium做同样的事情？

这很简单，我们只需要使用`driver.get`。因为Appium的客户端其实在是Selenium上做扩展的，所以我们可以直接使用Selenium的命令进行访问URL.在我们的例子中，URL的概念只是...稍微大了点。让我们使用用户名`darlene`和密码`testing123`来进行登录。我们要做的就是建立一个测试的会话，然后执行下面的命令
```java
driver.get("theapp://login/darlene/testing123");
```
当然了，构建响应URL和怎么执行正确操作这个是要靠开发人员实现的。我们需要做的是确保线上版本的app是没有这个功能的。但这个在测试期间，app支持deep link是很有必要的，因为能够设置任意测试状态是缩短测试时间的最佳方式，我们有必要去说服开发实现这些功能。在我测试The App的体验中，通过走deep link跳过登录，我发现每个测试用例我可以节约大概5~10秒。这的确节省了时间。

现在是完整的示例代码。这里介绍了两种测试登录后的页面正确性的方法。第一种是通过登录的UI上的操作，第二种是使用deep link。这个例子也给我们展示了Page Object大概是怎么样的，PO是一种可以解决代码复用的一种模式。然后你也会发现在测试Ios和Andoiod上我的代码只做了一些少量的改动，因为The App是跨平台的。

```java
import io.appium.java_client.AppiumDriver;
import io.appium.java_client.MobileBy;
import io.appium.java_client.android.AndroidDriver;
import io.appium.java_client.ios.IOSDriver;
import java.io.IOException;
import java.net.URL;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;
import org.openqa.selenium.By;
import org.openqa.selenium.remote.DesiredCapabilities;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

@RunWith(JUnit4.class)
public class Edition007_Deep_Linking {

    private String APP_IOS = "https://github.com/cloudgrey-io/the-app/releases/download/v1.2.1/TheApp-v1.2.1.app.zip";
    private String APP_ANDROID = "https://github.com/cloudgrey-io/the-app/releases/download/v1.2.1/TheApp-v1.2.1.apk";

    private String AUTH_USER = "alice";
    private String AUTH_PASS = "mypassword";

    @Test
    public void testLoginSlowIOS() throws IOException {
        IOSModel model = new IOSModel();
        IOSDriver driver = new IOSDriver<>(new URL("http://localhost:4723/wd/hub"), model.caps);
        runStepByStepTest(driver, model);
    }

    @Test
    public void testLoginSlowAndroid() throws IOException {
        AndroidModel model = new AndroidModel();
        AndroidDriver driver = new AndroidDriver(new URL("http://localhost:4723/wd/hub"), model.caps);
        runStepByStepTest(driver, model);
    }

    private void runStepByStepTest(AppiumDriver driver, Model model) {
        WebDriverWait wait = new WebDriverWait(driver, 10);

        try {
            wait.until(ExpectedConditions.presenceOfElementLocated(model.loginScreen)).click();
            wait.until(ExpectedConditions.presenceOfElementLocated(model.username)).sendKeys(AUTH_USER);
            wait.until(ExpectedConditions.presenceOfElementLocated(model.password)).sendKeys(AUTH_PASS);
            wait.until(ExpectedConditions.presenceOfElementLocated(model.loginBtn)).click();
            wait.until(ExpectedConditions.presenceOfElementLocated(model.getLoggedInBy(AUTH_USER)));
        } finally {
            driver.quit();
        }
    }

    @Test
    public void testDeepLinkForDirectNavIOS () throws IOException {
        IOSModel model = new IOSModel();
        IOSDriver driver = new IOSDriver<>(new URL("http://localhost:4723/wd/hub"), model.caps);
        runDeepLinkTest(driver, model);
    }

    @Test
    public void testDeepLinkForDirectNavAndroid () throws IOException {
        AndroidModel model = new AndroidModel();
        AndroidDriver driver = new AndroidDriver(new URL("http://localhost:4723/wd/hub"), model.caps);
        runDeepLinkTest(driver, model);
    }

    private void runDeepLinkTest(AppiumDriver driver, Model model) {
        WebDriverWait wait = new WebDriverWait(driver, 10);

        try {
            driver.get("theapp://login/" + AUTH_USER + "/" + AUTH_PASS);
            wait.until(ExpectedConditions.presenceOfElementLocated(model.getLoggedInBy(AUTH_USER)));
        } finally {
            driver.quit();
        }
    }

    private abstract class Model {
        public By loginScreen = MobileBy.AccessibilityId("Login Screen");
        public By loginBtn = MobileBy.AccessibilityId("loginBtn");
        public By username;
        public By password;

        public DesiredCapabilities caps;

        abstract By getLoggedInBy(String username);
    }

    private class IOSModel extends Model {
        IOSModel() {
            username = By.xpath("//XCUIElementTypeTextField[@name=\"username\"]");
            password = By.xpath("//XCUIElementTypeSecureTextField[@name=\"password\"]");

            caps = new DesiredCapabilities();
            caps.setCapability("platformName", "iOS");
            caps.setCapability("deviceName", "iPhone 7");
            caps.setCapability("platformVersion", "11.2");
            caps.setCapability("app", APP_IOS);
        }

        public By getLoggedInBy(String username) {
            return MobileBy.AccessibilityId("You are logged in as " + username);
        }
    }

    private class AndroidModel extends Model {
        AndroidModel() {
            username = MobileBy.AccessibilityId("username");
            password = MobileBy.AccessibilityId("password");

            caps = new DesiredCapabilities();
            caps.setCapability("platformName", "Android");
            caps.setCapability("deviceName", "Android Emulator");
            caps.setCapability("app", APP_ANDROID);
            caps.setCapability("automationName", "UiAutomator2");
        }

        public By getLoggedInBy(String username) {
            return By.xpath("//android.widget.TextView[@text=\"You are logged in as " + username + "\"]");
        }
    }
}

```