# Appium性能测试
习惯上来说，大家使用Appium一般都是用来验证手机app的功能，并且是通过手机应用UI界面的状态来确认手机应用功能的正确性。那通过自动化的方式我们不仅仅可以验证功能，我们还有其他很多用户体验的维护值得验证，性能就是其中之一。简单来说，对于用户要讲性能就是app的响应速度，包括从网络请求延时到CPU和内存的时候用情况。

相较于桌面应用，手机应用是运行在一个资源受限的环境中。手机应用可能会因为其本身运行在前端而会造成用户的体验度不高，也可能因为其占用CPU或者内存从而导致了电池寿命缩短或者造成其他app运行缓慢。所以进行性能测试是非常有必要的，它不仅仅保证了app本身的良好体验，也确保了手机的app生态环境。

幸运的是，Appium可以通过APi来获取到各种性能数据，至少安卓上是可以的。在通过adb dumpsys收集的大量信息的基础上，Appium可以通过`getPerformanceData`命令获取到应用程序性能的各个方面的简要信息。客户端的调用是很简单的，如下
```java
driver.getPerformanceData("<package>", "<perf type>", <timeout>);
```
<package>是我们的被测app包.<perf type>表示的是我们想要获取的性能数据类型。我们可以通过[getSupportedPerformanceDataTypes](https://appium.io/docs/en/commands/device/performance-data/performance-data-types/)来获取有效的类型，目前有，`cpuinfo`, `memoryinfo`, 'batteryinfo' 和`networkinfo`。最后<timeout>表示如果Appium不能立即获取到性能数据，等待的时间，它是一个整数.

性能是一个很复杂的话题，我们不可能在一个章节中就能挖掘玩。所以我们就专注于一个简单的例子，内存使用量。许多app都会在使用的历程中遇到的问题是内存泄漏。尽管生活在垃圾收集的环境中，Android应用仍然会导致内存被锁定为无法使用的状态。所以在测试应用在长期使用中内存是否有无缘无故增长内存使用时十分重要的。

让我们构造一个简单的场景来说明这一点，它很容易移植到您自己的Android应用程序中。首先，我们打开应用，记录下第一个时间点的内存使用量，然后等待一会儿，我们记录第二个时间点的内存使用量。然后我们通过比较第二次的内存量使用不比第一次的内存使用量大来断言我们的应用不存在内存泄漏。

假设我们使用的是ApiDemos这个APP应用，我们的调用将如下：
```java
List<List<Object>> data = driver.getPerformanceData("io.appium.android.apis", "memoryinfo", 10);
```
这条命令的返回值是两个列表，其中一个是键，另外一个是值。这里我们可以写一些帮助函数来帮我们可以获取到特定的内存数据(当然在现实世界中，我们将使用类来处理这些数据):
```java
private HashMap<String, Integer> getMemoryInfo(AndroidDriver driver) throws Exception {
    List<List<Object>> data = driver.getPerformanceData("io.appium.android.apis", "memoryinfo", 10);
    HashMap<String, Integer> readableData = new HashMap<>();
    for (int i = 0; i < data.get(0).size(); i++) {
        int val;
        if (data.get(1).get(i) == null) {
            val = 0;
        } else {
            val = Integer.parseInt((String) data.get(1).get(i));
        }
        readableData.put((String) data.get(0).get(i), val);
    }
    return readableData;
}
```
现在我们就可以用`HashMap`来获取到特定的内存使用的数据。我们将获取`totalPas`来做一个示范:
```java
HashMap<String, Integer> memoryInfo = getMemoryInfo(driver);
int setSize = memoryInfo.get("totalPss");
```
什么是`totalPas`？ PSS表示的是。根据[安卓dumpsys文档](https://developer.android.com/studio/command-line/dumpsys.html):
>这是对您应用的RAM使用情况的一种衡量，其中考虑了跨进程共享页面的情况。您的进程所独有的任何RAM页都直接贡献其PSS值，而与其他进程共享的页则仅与共享量成比例地贡献PSS值。例如，两个进程之间共享的页面将为每个进程的PSS贡献一半的大小。

换一句话说，对于我们appRAM影响这将是一个非常不错的测试手段。这里还有很多需要挖掘的东西，不过对于我们的case来说已经足够了。剩下来我们将这段内存检测嵌入到我们的代码中，然后做一些断言。下面是完成代码：
```java
import io.appium.java_client.android.AndroidDriver;
import java.io.File;
import java.net.URL;
import java.util.HashMap;
import java.util.List;
import org.hamcrest.Matchers;
import org.junit.Assert;
import org.junit.Test;
import org.openqa.selenium.remote.DesiredCapabilities;

public class Edition005_Android_Memory {

    private static int MEMORY_USAGE_WAIT = 30000;
    private static int MEMORY_CAPTURE_WAIT = 10;
    private static String PKG = "io.appium.android.apis";
    private static String PERF_TYPE = "memoryinfo";
    private static String PSS_TYPE = "totalPss";

    @Test
    public void testMemoryUsage() throws Exception {
        File classpathRoot = new File(System.getProperty("user.dir"));
        File appDir = new File(classpathRoot, "../apps/");
        File app = new File(appDir.getCanonicalPath(), "ApiDemos.apk");

        DesiredCapabilities capabilities = new DesiredCapabilities();
        capabilities.setCapability("platformName", "Android");
        capabilities.setCapability("deviceName", "Android Emulator");
        capabilities.setCapability("automationName", "UiAutomator2");
        capabilities.setCapability("app", app);

        AndroidDriver driver = new AndroidDriver(new URL("http://localhost:4723/wd/hub"), capabilities);

        try {
            // get the usage at one point in time
            int totalPss1 = getMemoryInfo(driver).get(PSS_TYPE);

            // then get it again after waiting a while
            try { Thread.sleep(MEMORY_USAGE_WAIT); } catch (InterruptedException ign) {}
            int totalPss2 = getMemoryInfo(driver).get(PSS_TYPE);

            // finally, verify that we haven't increased usage more than 5%
            Assert.assertThat((double) totalPss2, Matchers.lessThan(totalPss1 * 1.05));
        } finally {
            driver.quit();
            }
        }

        private HashMap<String, Integer> getMemoryInfo(AndroidDriver driver) throws Exception {
        List<List<Object>> data = driver.getPerformanceData(PKG, PERF_TYPE, MEMORY_CAPTURE_WAIT);
        HashMap<String, Integer> readableData = new HashMap<>();
        for (int i = 0; i < data.get(0).size(); i++) {
            int val;
            if (data.get(1).get(i) == null) {
            val = 0;
            } else {
                val = Integer.parseInt((String) data.get(1).get(i));
            }
            readableData.put((String) data.get(0).get(i), val);
        }
        return readableData;
    }
}
```

我衷心建议您对应用程序进行一些自动化性能测试。即便是使用类似于上述这样简单的测试，我们都可以发现一些影响用户体验的问题，即便我们没有发现功能问题。请继续关注有关Appium在以后版本中进行的性能测试或其他类型测试的更多讨论。

最后惯例补上python的代码:
```python
from appium import webdriver

caps = {}
caps['platformName'] = 'Android'
caps['deviceName'] = 'Google Pixel'
caps['automationName'] = 'UiAutomator2'
caps['appPackage'] = 'com.android.gallery3d'
caps['appActivity'] = 'com.android.gallery3d.app.GalleryActivity'

driver = webdriver.Remote("http://localhost:4723/wd/hub", caps)

result = driver.get_performance_data('com.android.gallery3d', 'memoryinfo', 5)
print(result)
```
输出结果是:
```python
[
    ['totalPrivateDirty', 'nativePrivateDirty', 'dalvikPrivateDirty', 'eglPrivateDirty', 'glPrivateDirty', 'totalPss', 'nativePss', 'dalvikPss', 'eglPss', 'glPss', 'nativeHeapAllocatedSize', 'nativeHeapSize'], 

    ['9548', '5728', '1256', None, None, '19031', '5800', '1324', None, None, '16963', '19200']
]
```
