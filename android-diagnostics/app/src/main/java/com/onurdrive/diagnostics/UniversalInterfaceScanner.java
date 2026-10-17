package com.onurdrive.diagnostics;

import android.content.Context;
import android.content.pm.PackageManager;
import android.graphics.SurfaceTexture;
import android.hardware.camera2.CameraCharacteristics;
import android.hardware.camera2.CameraManager;
import android.hardware.camera2.params.StreamConfigurationMap;
import android.hardware.usb.UsbDevice;
import android.hardware.usb.UsbManager;
import android.os.Build;
import android.util.Size;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.Arrays;
import java.util.Locale;
import java.util.Map;
import org.json.JSONArray;
import org.json.JSONObject;

/**
 * Cross-brand read-only inventory of PUBLIC app-visible Android camera and Linux
 * video interfaces. Does not open V4L2/EVS, execute shell commands, request root,
 * inspect vehicle buses or modify an automotive control.
 *
 * Visibility never implies capture permission; an empty result never proves
 * that physical cameras do not exist.
 */
public final class UniversalInterfaceScanner {
    private UniversalInterfaceScanner() { }

    public static JSONObject scan(Context context) {
        JSONObject root = new JSONObject();
        try {
            root.put("schema_version", "1.0");
            root.put("scan_type", "PUBLIC_READ_ONLY_INTERFACE_INVENTORY");
            root.put("created_at_utc", new java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US)
                    {{ setTimeZone(java.util.TimeZone.getTimeZone("UTC")); }}
                    .format(new java.util.Date()));
            root.put("vehicle_model", "NOT_AUTO_IDENTIFIABLE_FROM_STANDARD_ANDROID_APIS");
            root.put("installation", "USER_MUST_CONFIRM_DEVICE_IS_VEHICLE_HEAD_UNIT");
            root.put("access_scope", "ANDROID_APP_UID_ONLY");
            root.put("no_root_or_can_or_oem_write", true);
            root.put("device", deviceInfo(context));
            root.put("camera2", camera2Info(context));
            root.put("linux_video", linuxVideoInfo());
            root.put("usb_inventory", usbInfo(context));
            root.put("interpretation", interpretation(root));
            root.put("safety_notice",
                "Device paths are discovery hints only. Hidden system cameras, privileged EVS interfaces, "
              + "video codecs and physical cable pinouts cannot be discovered by a normal app. "
              + "Do not alter AVM/ADAS camera operating constraints or try this while driving.");
        } catch (Exception e) {
            put(root, "scanner_error", e.getClass().getSimpleName());
        }
        return root;
    }

    private static JSONObject deviceInfo(Context ctx) {
        JSONObject o = new JSONObject();
        put(o,"manufacturer",Build.MANUFACTURER);
        put(o,"model",Build.MODEL);
        put(o,"brand",Build.BRAND);
        put(o,"board",Build.BOARD);
        put(o,"device",Build.DEVICE);
        put(o,"product",Build.PRODUCT);
        put(o,"hardware",Build.HARDWARE);
        put(o,"android_release",Build.VERSION.RELEASE);
        put(o,"sdk",Build.VERSION.SDK_INT);
        // Automotive FEATURE_AUTOMOTIVE is not present in many customized Android head units.
        put(o,"android_automotive_feature",
            ctx.getPackageManager().hasSystemFeature(PackageManager.FEATURE_AUTOMOTIVE));
        return o;
    }

    private static JSONObject camera2Info(Context ctx) {
        JSONObject o = new JSONObject();
        JSONArray found = new JSONArray();
        put(o,"api","Camera2 / normal Android app UID");
        CameraManager manager = (CameraManager)ctx.getSystemService(Context.CAMERA_SERVICE);
        try {
            if (manager == null) {
                put(o,"enumeration","NO_CAMERA_SERVICE");
            } else {
                String[] ids = manager.getCameraIdList();
                put(o,"enumeration","OK");
                put(o,"count",ids.length);
                for (String id: ids) {
                    JSONObject camera = new JSONObject();
                    put(camera,"id",id);
                    try {
                        CameraCharacteristics ch=manager.getCameraCharacteristics(id);
                        put(camera,"lens_facing",String.valueOf(ch.get(CameraCharacteristics.LENS_FACING)));
                        put(camera,"orientation_deg",ch.get(CameraCharacteristics.SENSOR_ORIENTATION));
                        put(camera,"hardware_level",ch.get(CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL));
                        int[] capabilities=ch.get(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES);
                        JSONArray caps=new JSONArray();
                        if (capabilities!=null) for (int c: capabilities) caps.put(c);
                        put(camera,"available_capabilities",caps);
                        if (Build.VERSION.SDK_INT>=28) {
                            JSONArray physical=new JSONArray();
                            for(String subId:ch.getPhysicalCameraIds()) physical.put(subId);
                            put(camera,"physical_camera_ids",physical);
                        }
                        StreamConfigurationMap config=ch.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP);
                        JSONArray dims=new JSONArray();
                        if(config!=null) {
                            Size[] sizes=config.getOutputSizes(SurfaceTexture.class);
                            if(sizes!=null) {
                                for(int i=0;i<Math.min(20,sizes.length);i++) {
                                    dims.put(sizes[i].getWidth()+"x"+sizes[i].getHeight());
                                }
                            }
                        }
                        put(camera,"surface_texture_sizes_up_to_20",dims);
                    } catch (Exception inner) {
                        put(camera,"metadata_error",inner.getClass().getSimpleName());
                    }
                    found.put(camera);
                }
            }
        } catch (Exception e) {
            put(o,"enumeration","ACCESS_DENIED_OR_UNAVAILABLE");
            put(o,"error",e.getClass().getSimpleName());
        }
        put(o,"devices",found);
        put(o,"meaning","Enumerated cameras are not proof that live frames can be captured.");
        return o;
    }

    private static JSONObject linuxVideoInfo() {
        JSONObject o=new JSONObject();
        JSONArray nodes=new JSONArray();
        JSONArray sysfs=new JSONArray();
        // No read() or open() on video devices: merely list visible entries and OS mode hints.
        scanNames(new File("/dev"),nodes,"video","media","v4l-subdev");
        File videoClass=new File("/sys/class/video4linux");
        File[] entries=videoClass.listFiles();
        if (entries!=null) {
            Arrays.sort(entries,(a,b)->a.getName().compareTo(b.getName()));
            for(int i=0;i<Math.min(48,entries.length);i++) {
                File f=entries[i];
                JSONObject d=new JSONObject();
                put(d,"node",f.getName());
                put(d,"name",readLimited(new File(f,"name"),128));
                sysfs.put(d);
            }
            put(o,"sysfs_listing","READABLE");
        } else {
            put(o,"sysfs_listing",videoClass.exists()?"NOT_READABLE":"NOT_PRESENT");
        }
        put(o,"dev_nodes",nodes);
        put(o,"sysfs_video4linux",sysfs);
        put(o,"note","OS file canRead is only a hint; SELinux, driver access or stream availability is unverified.");
        return o;
    }

    private static void scanNames(File parent, JSONArray out, String... prefixes) {
        File[] files=parent.listFiles();
        if(files==null) return;
        Arrays.sort(files,(a,b)->a.getName().compareTo(b.getName()));
        int included=0;
        for(File f:files) {
            boolean matches=false;
            for(String prefix:prefixes) {
                if(f.getName().matches(java.util.regex.Pattern.quote(prefix)+"[0-9]+")) {
                    matches=true;break;
                }
            }
            if(!matches) continue;
            JSONObject node=new JSONObject();
            put(node,"path",f.getAbsolutePath());
            put(node,"exists",f.exists());
            put(node,"java_can_read_hint",f.canRead());
            put(node,"java_can_write_hint",f.canWrite()); // report only, never write
            out.put(node);
            if(++included>=48) break;
        }
    }

    private static String readLimited(File file,int maxChars) {
        if(!file.canRead()) return "NOT_READABLE";
        try(BufferedReader reader=new BufferedReader(new FileReader(file))) {
            char[] data=new char[maxChars];
            int len=reader.read(data);
            return len>0?new String(data,0,len).trim():"EMPTY";
        } catch(IOException | SecurityException e) {
            return "READ_ERROR_"+e.getClass().getSimpleName();
        }
    }

    private static JSONObject usbInfo(Context ctx) {
        JSONObject o=new JSONObject();
        JSONArray devices=new JSONArray();
        try {
            UsbManager manager=(UsbManager)ctx.getSystemService(Context.USB_SERVICE);
            if(manager==null) {
                put(o,"enumeration","SERVICE_NOT_PRESENT");
            } else {
                for(UsbDevice d:manager.getDeviceList().values()) {
                    JSONObject item=new JSONObject();
                    put(item,"vendor_id",d.getVendorId());
                    put(item,"product_id",d.getProductId());
                    put(item,"device_class",d.getDeviceClass());
                    put(item,"interface_count",d.getInterfaceCount());
                    devices.put(item);
                }
                put(o,"enumeration","OK");
            }
        } catch(Exception e) {
            put(o,"enumeration","ACCESS_DENIED_OR_UNAVAILABLE");
            put(o,"error",e.getClass().getSimpleName());
        }
        put(o,"devices",devices);
        put(o,"note","USB listing is not evidence of factory camera wiring or camera stream accessibility.");
        return o;
    }

    private static JSONObject interpretation(JSONObject root) {
        JSONObject result=new JSONObject();
        JSONObject cam=root.optJSONObject("camera2");
        JSONObject linux=root.optJSONObject("linux_video");
        boolean cameraVisible=cam!=null&&cam.optJSONArray("devices")!=null&&cam.optJSONArray("devices").length()>0;
        boolean nodeVisible=linux!=null&&linux.optJSONArray("dev_nodes")!=null&&linux.optJSONArray("dev_nodes").length()>0;
        put(result,"public_camera2_devices_visible",cameraVisible);
        put(result,"linux_video_nodes_visible",nodeVisible);
        put(result,"live_factory_camera_access_verified",false);
        put(result,"supported_action",cameraVisible?
                "Try explicit parked Camera2 preview, verify frames.":
                "No public Camera2 camera found. OEM pathways still unknown.");
        put(result,"oem_evs_access","NOT_CHECKABLE_WITH_NORMAL_APP_PERMISSIONS");
        put(result,"camera_stream_after_oem_speed_cutoff","NOT_TESTED");
        return result;
    }

    private static void put(JSONObject target,String key,Object value) {
        try {target.put(key,value);}catch(Exception ignored) {}
    }
}
