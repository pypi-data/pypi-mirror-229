from setuptools import setup, find_packages

setup(
    name='ssai',
    version='1.0.4',
    description="SuperSummarizeAI is a versatile Python tool designed to extract and summarize textual content. Whether it's from a provided webpage URL, a YouTube video link, or a PDF file, this tool processes the content through ChatGPT to generate an insightful summary. Once the summary is ready, the tool copies the content directly to your clipboard for quick access and sharing. Additionally, with its multilingual capabilities, SuperSummarizeAI can cater to a global audience, generating summaries in various languages.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Alexandre Lima',
    author_email='alexandrevl@gmail.com',
    url='https://github.com/alexandrevl/SuperSummarizeAI',
    packages=find_packages(),
    install_requires=open('requirements.txt').readlines(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    entry_points={
        'console_scripts': [
            'ssai=ssai:ssai',
        ],
    },
)

