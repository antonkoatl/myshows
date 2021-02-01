import imageio
import numpy as np
from django.core.files import File
from skimage.color import grey2rgb
from skimage.transform import resize
from skimage.util import crop

from demo import load_checkpoints, make_animation
from skimage import img_as_ubyte
import warnings

warnings.filterwarnings("ignore")


def resize_padded(img, new_shape, fill_cval=None, order=1):
    if fill_cval is None:
        fill_cval = np.max(img)
    if len(img.shape) == 2: img = grey2rgb(img)

    ratio = np.min([n / i for n, i in zip(new_shape, img.shape)])
    interm_shape = np.rint([s * ratio if i < len(img.shape) - 1 else s for i, s in enumerate(img.shape)]).astype(np.int)
    interm_img = resize(img, interm_shape, order=order, cval=fill_cval)

    new_img = np.empty((new_shape[0], new_shape[1], img.shape[2]), dtype=interm_img.dtype)
    new_img.fill(fill_cval)

    pad = [((n - s) >> 1, ((n - s) >> 1) + ((n - s) % 2)) for n, s in zip(new_shape, interm_shape)]
    new_img[[slice(p[0], -p[1], None) if 0 != p[0] else slice(None, None, None) for p in pad]] = interm_img

    new_img = np.clip(new_img, 0, 1)

    return new_img, interm_shape


def crop(img, shape):
    sx = int(max((img.shape[0] - shape[0]) / 2, 0))
    ex = int(img.shape[0] - sx)
    sy = int(max((img.shape[1] - shape[1]) / 2, 0))
    ey = int(img.shape[1] - sy)
    return img[sx:ex, sy:ey, :]


def animate(image_path):
    generator, kp_detector = load_checkpoints(config_path='config/vox-adv-256.yaml', checkpoint_path='vox-adv-cpk.pth.tar')

    source_image = imageio.imread(image_path)
    driving_video = imageio.mimread('drive.mp4')

    source_image, interm_shape = resize_padded(source_image, (256, 256))
    driving_video = [resize(frame, (256, 256))[..., :3] for frame in driving_video]

    predictions = make_animation(source_image, driving_video, generator, kp_detector, relative=True)
    predictions = [crop(x, interm_shape) for x in predictions]

    imageio.mimsave('output.mp4', [img_as_ubyte(frame) for frame in predictions], fps=30)

    return 'output.mp4'


def process_db():
    import django, os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    django.setup()

    from myshows.models import Show

    for i, show in enumerate(Show.objects.order_by('pk')):
        for person_role in show.personrole_set.filter(role='actor')[:5]:
            person = person_role.person
            if person.animated_poster.name is None and person.personimage_set.count() > 0:
                image_path = person.personimage_set.first().image.path
                video_path = animate(image_path)
                person.animated_poster.save(str(person.id) + '.' + video_path.split('.')[-1], File(open(video_path, 'rb')))
                print(person.animated_poster)
        print(f"{i} {show} ok")


if __name__ == "__main__":
    process_db()

