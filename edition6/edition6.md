# 测试IOS应用的升级功能
这周我们重新拥抱IOS的世界，谈论一下测试IOS的应用升级相关内容。对于许多测试人员除了在固定版本测试app的功能外，我们还会有一个共同的需求，就是当团队以一定频率对外更新版本时，我们是需要测试设备的升级。因为当我们对外发布新版本时，我们的用户会可能升级到最新的版本，而不是从原始版本开始安装。这就意味着我们的应用可能会存在各种各样的用户数据需要迁移从而保证应用可以正确运行，如果我们仅仅在最新版测试，那么我们将不会覆盖到这种场景从而遗漏缺陷。

幸运的是，Appium 1.8版本现在已经有一些命令可以使我们非常方便的在一个Appium会话中重新安装应用，重新启动应用。这就为我们验证升级提供了可能性。

为了演示这个功能，我首先先介绍一款App[The app](https://github.com/cloudgrey-io/the-app), 它是一个跨平台的， 用React Native编写的示例应用。我将用这个app在后续的示例中充当被测App。可能这个名字你听起来有点熟悉，这是因为我这里学了我的好朋友Dave Haeffner，对定冠词的使用(Dave Haeffner他是[Elemental Selenium](http://elementalselenium.com/)的作者，并且他写了一个示例的web app也用叫做[The Internet](https://the-internet.herokuapp.com/))。幸运的是，Dave慷慨地将名字创意捐赠给Appium Pro，这样我们就可以不用担心了。

我最近发布了一个版本，版本号是v1.0.0,这个应用目前只有一个特性，他会保存你在一个文本框中输入的文字，然后在界面上显示它。在程序内部，应用是通过`@TheApp:savedEcho`这个关键字去保存数据的。

现在，让我们假设，如果有一些疯狂的开发者决定修改这个关键字，使用`@TheApp:savedAwesomeText`去保存数据。这意味着如果我们只是简单的从旧版本升级到当前这个版本的话，app将无法通过新的关键字去找到在老版本中保存的数据。换言之，这一次的升级会十分影响用户对这款App的用户体验。在这种情况下，app就需要一段迁移代码，目的是将以旧的关键字保存的时候可以通过新关键字来访问。

这些都是开发者应该背负的责任。现在假设我们忘记编写了迁移代码，并且直接修改了这个关键字。然后我发布了版本v1.0.1。虽然如果用户只是在当前版本使用时没问题的，但是这个版本将会因为我们没有写迁移代码而存在一个bug。让我们继续假设，发生了很多事情之后，我编写了迁移代码，然后发布了v1.0.2。现在一个对我程序功能不放心的测试人员想要编写一个自动化测试用于验证升级到v1.0.2程序将不会出现问题(当然，他们自己也很沮丧，他们在v1.0.1发布之前没有编写过这样的升级测试)。

那我们怎么使用Appium的代码来完成这个功能？基本上来说，我们将利用下面三条`mobile:`方法：
```java
driver.executeScript("mobile: terminateApp", args);

driver.executeScript("mobile: installApp", args);

driver.executeScript("mobile: launchApp", args);
```
上述的命令集会先停止当前的app(这里一定要执行，这样的话底层的WebDriverAgent实例才不会认为当前app是崩溃了)，覆盖安装新的app，然后启动这个新的app。

那这里的`args`分别是什么呢？在每一个例子中每一个args都是一个`HashMap`对象，它用来生成一个简单的Json结构。`terminateApp`和`launchApp`命令中有一个键,`bundleId`(app的bundle Id)。`installApp`将使用`app`这个键，它表示新的app的路径或者是URL。

在我们的例子中，我们将使用两个版本的app:v1.0.0和v1.0.2来通过测试.
```java
private String APP_V1_0_0 = "https://github.com/cloudgrey-io/the-app/releases/download/v1.0.0/TheApp-v1.0.0.app.zip";
private String APP_V1_0_2 = "https://github.com/cloudgrey-io/the-app/releases/download/v1.0.2/TheApp-v1.0.2.app.zip";
```
我很高兴在Appium中可以使用Github上的链接来提供app的下载路径。假设我们使用v1.0.0的来作为我们启动Appium的`app`的capability，然后升级的命令将会像下面这样:
```java
import io.appium.java_client.MobileBy;
import io.appium.java_client.ios.IOSDriver;
import java.io.IOException;
import java.net.URL;
import java.util.HashMap;
import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;
import org.openqa.selenium.By;
import org.openqa.selenium.remote.DesiredCapabilities;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

@RunWith(JUnit4.class)
public class Edition006_iOS_Upgrade {

    private String BUNDLE_ID = "io.cloudgrey.the-app";

    private String APP_V1_0_0 = "https://github.com/cloudgrey-io/the-app/releases/download/v1.0.0/TheApp-v1.0.0.app.zip";
    private String APP_V1_0_1 = "https://github.com/cloudgrey-io/the-app/releases/download/v1.0.1/TheApp-v1.0.1.app.zip";
    private String APP_V1_0_2 = "https://github.com/cloudgrey-io/the-app/releases/download/v1.0.2/TheApp-v1.0.2.app.zip";

    private By msgInput = By.xpath("//XCUIElementTypeTextField[@name=\"messageInput\"]");
    private By savedMsg = MobileBy.AccessibilityId("savedMessage");
    private By saveMsgBtn = MobileBy.AccessibilityId("messageSaveBtn");
    private By echoBox = MobileBy.AccessibilityId("Echo Box");

    private String TEST_MESSAGE = "Hello World";

    @Test
    public void testSavedTextAfterUpgrade () throws IOException {
        DesiredCapabilities capabilities = new DesiredCapabilities();


        capabilities.setCapability("platformName", "iOS");
        capabilities.setCapability("deviceName", "iPhone 7");
        capabilities.setCapability("platformVersion", "11.2");
        capabilities.setCapability("app", APP_V1_0_0);

        // change this to APP_V1_0_1 to experience a failing scenario
        String appUpgradeVersion = APP_V1_0_2;

        // Open the app.
        IOSDriver driver = new IOSDriver<>(new URL("http://localhost:4723/wd/hub"), capabilities);

        WebDriverWait wait = new WebDriverWait(driver, 10);

        try {
            wait.until(ExpectedConditions.presenceOfElementLocated(echoBox)).click();
            wait.until(ExpectedConditions.presenceOfElementLocated(msgInput)).sendKeys(TEST_MESSAGE);
            wait.until(ExpectedConditions.presenceOfElementLocated(saveMsgBtn)).click();
            String savedText = wait.until(ExpectedConditions.presenceOfElementLocated(savedMsg)).getText();
            Assert.assertEquals(savedText, TEST_MESSAGE);

            HashMap<String, String> bundleArgs = new HashMap<>();
            bundleArgs.put("bundleId", BUNDLE_ID);
            driver.executeScript("mobile: terminateApp", bundleArgs);

            HashMap<String, String> installArgs = new HashMap<>();
            installArgs.put("app", appUpgradeVersion);
            driver.executeScript("mobile: installApp", installArgs);

            driver.executeScript("mobile: launchApp", bundleArgs);

            wait.until(ExpectedConditions.presenceOfElementLocated(echoBox)).click();
            savedText = wait.until(ExpectedConditions.presenceOfElementLocated(savedMsg)).getText();
            Assert.assertEquals(savedText, TEST_MESSAGE);
        } finally {
            driver.quit();
        }
    }
}

```

我们可以在[github](https://github.com/cloudgrey-io/appiumpro/blob/master/java/src/test/java/Edition006_iOS_Upgrade.java)上找到这段代码，这就是在IOS上测试应用升级的功能。在后续的专栏中我们将说明如何在安卓设备上验证应用的升级功能。