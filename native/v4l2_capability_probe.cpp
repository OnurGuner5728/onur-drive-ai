// Onur Drive AI - read-only V4L2 capability inventory. Linux-only.
// Opens one explicitly named node O_RDONLY; no STREAMON, S_FMT, controls, writes.
// Never run against a vehicle while moving. No claim of MG HS compatibility.
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <iostream>
#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <unistd.h>

int main(int argc, char** argv) {
    if (argc != 2) { std::cerr << "Usage: v4l2_capability_probe /dev/videoN\n"; return 2; }
    const char *name=argv[1];
    if (std::strncmp(name,"/dev/video",10)!=0) {
        std::cerr << "Only explicit /dev/videoN is allowed\n";return 2;
    }
    for(const char *p=name+10; *p; ++p) if(*p<'0'||*p>'9') {
        std::cerr << "Malformed V4L2 path\n";return 2;
    }
    if(name[10]=='\0')return 2;
    int fd=open(name,O_RDONLY|O_NONBLOCK|O_CLOEXEC|O_NOFOLLOW);
    if(fd<0){std::cerr << "Access denied or node not present: " << std::strerror(errno) << "\n";return 3;}
    v4l2_capability c{};
    if(ioctl(fd,VIDIOC_QUERYCAP,&c)<0){std::cerr << "QUERYCAP unavailable\n";close(fd);return 4;}
    std::cout<<"device="<<name<<" driver="<<c.driver<<" card="<<c.card<<"\n";
    std::cout<<"caps="<<c.capabilities<<" device_caps="<<c.device_caps<<"\n";
    for(unsigned type: {V4L2_BUF_TYPE_VIDEO_CAPTURE, V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE}) {
        for(unsigned i=0;i<40;++i) {
            v4l2_fmtdesc desc{};
            desc.index=i;desc.type=type;
            if(ioctl(fd,VIDIOC_ENUM_FMT,&desc)<0)break;
            std::cout<<"type="<<type<<" format="<<desc.description<<"\n";
        }
    }
    close(fd);
    return 0;
}
